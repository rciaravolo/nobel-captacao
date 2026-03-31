import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.57.4";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY')!;
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

    // ═══════════════════════════════════════════════════════════════════════════
    // AUTHENTICATION: Verify user is logged in
    // ═══════════════════════════════════════════════════════════════════════════
    const authHeader = req.headers.get('Authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      console.error('Authentication failed: No authorization header');
      return new Response(
        JSON.stringify({ error: 'Não autorizado - Faça login para continuar' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Create client with user's token to verify authentication
    const supabaseAuth = createClient(supabaseUrl, supabaseAnonKey, {
      global: { headers: { Authorization: authHeader } }
    });

    const token = authHeader.replace('Bearer ', '');
    const { data: claimsData, error: claimsError } = await supabaseAuth.auth.getUser(token);

    if (claimsError || !claimsData?.user) {
      console.error('Authentication failed:', claimsError?.message || 'Invalid token');
      return new Response(
        JSON.stringify({ error: 'Token inválido ou expirado' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const userId = claimsData.user.id;
    console.log('Authenticated user:', userId, claimsData.user.email);

    // ═══════════════════════════════════════════════════════════════════════════
    // AUTHORIZATION: Verify user has admin role
    // ═══════════════════════════════════════════════════════════════════════════
    const { data: roleData, error: roleError } = await supabaseAuth
      .rpc('has_role', { _user_id: userId, _role: 'admin' });

    if (roleError) {
      console.error('Error checking admin role:', roleError);
      return new Response(
        JSON.stringify({ error: 'Erro ao verificar permissões' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!roleData) {
      console.error('Authorization failed: User', userId, 'is not an admin');
      return new Response(
        JSON.stringify({ error: 'Acesso negado - Apenas administradores podem executar esta ação' }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('Admin authorization confirmed for user:', claimsData.user.email);

    // ═══════════════════════════════════════════════════════════════════════════
    // BUSINESS LOGIC: Process request (only reached if admin)
    // ═══════════════════════════════════════════════════════════════════════════
    const { pdfContent, monthYear, deleteOnly, insertProducts, mirrorProfile } = await req.json();
    
    if (!monthYear) {
      return new Response(
        JSON.stringify({ error: 'month_year is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Use service role key for database operations (bypasses RLS for admin operations)
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Handle delete-only operation
    if (deleteOnly) {
      console.log('Admin', claimsData.user.email, 'deleting products for:', monthYear);

      const { error: deleteError } = await supabase
        .from('recommended_products')
        .delete()
        .eq('month_year', monthYear);

      if (deleteError) {
        console.error('Error deleting products:', deleteError);
        throw deleteError;
      }

      console.log(`Deleted products for ${monthYear}`);

      return new Response(
        JSON.stringify({ 
          success: true, 
          message: `Products for ${monthYear} deleted successfully`
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Handle mirror profile operation - copy products from one profile to another
    if (mirrorProfile) {
      const { sourceProfile, targetProfile } = mirrorProfile;
      console.log('Admin', claimsData.user.email, `mirroring products from ${sourceProfile} to ${targetProfile} for ${monthYear}`);

      // Get products from source profile
      const { data: sourceProducts, error: fetchError } = await supabase
        .from('recommended_products')
        .select('*')
        .eq('month_year', monthYear)
        .eq('profile', sourceProfile);

      if (fetchError) {
        console.error('Error fetching source products:', fetchError);
        throw fetchError;
      }

      if (!sourceProducts || sourceProducts.length === 0) {
        return new Response(
          JSON.stringify({ error: `No products found for profile ${sourceProfile}` }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // Delete existing products for target profile
      const { error: deleteError } = await supabase
        .from('recommended_products')
        .delete()
        .eq('month_year', monthYear)
        .eq('profile', targetProfile);

      if (deleteError) {
        console.error('Error deleting target products:', deleteError);
        throw deleteError;
      }

      // Insert products with new profile
      const productsToInsert = sourceProducts.map((p: any) => ({
        month_year: monthYear,
        asset_class: p.asset_class,
        asset_subclass: p.asset_subclass,
        product_name: p.product_name,
        percentage: p.percentage,
        expected_return: p.expected_return,
        eligibility: p.eligibility,
        product_type: p.product_type,
        profile: targetProfile
      }));

      const { data, error: insertError } = await supabase
        .from('recommended_products')
        .insert(productsToInsert)
        .select();

      if (insertError) {
        console.error('Error inserting mirrored products:', insertError);
        throw insertError;
      }

      console.log(`Successfully mirrored ${data?.length || 0} products to ${targetProfile}`);

      return new Response(
        JSON.stringify({ 
          success: true, 
          message: `Mirrored ${data?.length || 0} products from ${sourceProfile} to ${targetProfile}`,
          products_count: data?.length || 0
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Handle direct insert operation
    if (insertProducts && Array.isArray(insertProducts)) {
      console.log('Admin', claimsData.user.email, `inserting ${insertProducts.length} products for ${monthYear}`);

      const productsToInsert = insertProducts.map((p: any) => ({
        month_year: monthYear,
        asset_class: p.asset_class,
        asset_subclass: p.asset_subclass,
        product_name: p.product_name,
        percentage: p.percentage || null,
        expected_return: p.expected_return || null,
        eligibility: p.eligibility || null,
        product_type: p.product_type || null,
        profile: p.profile
      }));

      const { data, error: insertError } = await supabase
        .from('recommended_products')
        .insert(productsToInsert)
        .select();

      if (insertError) {
        console.error('Error inserting products:', insertError);
        throw insertError;
      }

      console.log(`Successfully inserted ${data?.length || 0} products`);

      return new Response(
        JSON.stringify({ 
          success: true, 
          products_count: data?.length || 0,
          products: data
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!pdfContent) {
      return new Response(
        JSON.stringify({ error: 'PDF content is required for parsing' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error('LOVABLE_API_KEY not configured');
    }

    console.log('Admin', claimsData.user.email, 'parsing allocation materials for:', monthYear);

    // Use Lovable AI with tool calling to extract structured product data
    const response = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'google/gemini-2.5-flash',
        messages: [
          {
            role: 'system',
            content: `Você é um especialista em análise de materiais de alocação de investimentos. Extraia informações estruturadas de produtos recomendados de PDFs da XP.`
          },
          {
            role: 'user',
            content: `Analise o seguinte conteúdo de PDF e extraia TODOS os produtos recomendados com suas informações:

${pdfContent}

INSTRUÇÕES CRÍTICAS - LEIA COM ATENÇÃO:

═══════════════════════════════════════════════════════════════════════════
1. NOME COMPLETO DO PRODUTO (product_name)
═══════════════════════════════════════════════════════════════════════════
O campo "product_name" DEVE conter o nome ESPECÍFICO e COMPLETO do produto conforme aparece no PDF.
NUNCA use apenas o tipo genérico como "CRI", "CDB", "Fundo".

✅ EXEMPLOS CORRETOS:
- "XP Referenciado FI Referenciado DI CP" (não apenas "Fundo")
- "CRI BTG (98,5% CDI)" (não apenas "CRI")
- "NTN-B 2030" (não apenas "Título Público")
- "CDII11" (não apenas "FII")

═══════════════════════════════════════════════════════════════════════════
2. CLASSE DE ATIVO (asset_class) - USE EXATAMENTE ESTAS:
═══════════════════════════════════════════════════════════════════════════
Identifique a classe e use EXATAMENTE um destes valores:

• "RENDA FIXA BRASIL" → Para CRI, CRA, CDB, LCI, LCA, Debêntures, Títulos Públicos, Fundos DI
• "RENDA VARIÁVEL BRASIL" → Para ações brasileiras e fundos de ações brasileiras
• "RENDA FIXA GLOBAL" → Para títulos e fundos de renda fixa internacional
• "RENDA VARIÁVEL GLOBAL" → Para ações internacionais e fundos globais
• "MULTIMERCADO" → Para fundos multimercado
• "FUNDOS LISTADOS" → Para ETFs e FIIs
• "ALTERNATIVOS" → Para COE, estruturados, private equity

IMPORTANTE: Um CRI, CRA, CDB, Debênture SEMPRE vai na classe "RENDA FIXA BRASIL"!

═══════════════════════════════════════════════════════════════════════════
3. SUBCLASSE (asset_subclass) - NORMALIZE CORRETAMENTE:
═══════════════════════════════════════════════════════════════════════════
Baseado na CLASSE identificada, use a subclasse apropriada:

Para "RENDA FIXA BRASIL":
  • "Pós-fixado" → CDB CDI, LCI CDI, fundos DI
  • "Inflação" → CRI IPCA+, Debêntures IPCA+, NTN-B
  • "Prefixado" → CDB prefixado, LCI prefixado

Para "RENDA VARIÁVEL BRASIL":
  • "Ações Brasil" → Ações individuais
  • "Fundo de Ações" → Fundos de ações

Para "MULTIMERCADO":
  • "Fundo Multimercado" → Fundos multimercado
  • "Previdência" → Fundos de previdência

Para "FUNDOS LISTADOS":
  • Use o nome específico do fundo ou "ETF" ou "FII"

Para "ALTERNATIVOS":
  • Use o tipo específico como "COE", "Estruturado", etc.

═══════════════════════════════════════════════════════════════════════════
4. PERFIL DO INVESTIDOR (profile)
═══════════════════════════════════════════════════════════════════════════
O documento contém produtos para 3 perfis. Identifique baseado nas seções/tabelas:

• "conservative" → Carteira Conservadora, Perfil Conservador
• "moderate" → Carteira Moderada, Perfil Moderado
• "sophisticated" → Carteira Sofisticada, Perfil Sofisticado, Carteira Agressiva

Se um produto aparece em múltiplos perfis com percentuais diferentes, crie uma entrada separada para cada perfil.

═══════════════════════════════════════════════════════════════════════════
5. OUTROS CAMPOS OBRIGATÓRIOS:
═══════════════════════════════════════════════════════════════════════════
• percentage: O percentual de alocação (ex: 6.0 para 6,0%)
• expected_return: Exatamente como aparece (ex: "6,0%", "CDI + 2,5%", "IPCA + 10%")
• eligibility: "PG" ou "IQ" conforme indicado no PDF
• product_type: Tipo genérico (CRI, CRA, CDB, Fundo, Debênture, FII, etc.)

═══════════════════════════════════════════════════════════════════════════
EXEMPLO COMPLETO DE EXTRAÇÃO:
═══════════════════════════════════════════════════════════════════════════
Se o PDF mostra na tabela "Carteira Moderada":
"RENDA FIXA | Inflação | XP Referenciado FI Referenciado DI CP | 6,0% | 6,0% | PG"

Extraia assim:
{
  "asset_class": "RENDA FIXA BRASIL",
  "asset_subclass": "Pós-fixado",
  "product_name": "XP Referenciado FI Referenciado DI CP",
  "percentage": 6.0,
  "expected_return": "6,0%",
  "eligibility": "PG",
  "product_type": "Fundo",
  "profile": "moderate"
}

COMECE A EXTRAÇÃO AGORA!`
          }
        ],
        tools: [
          {
            type: 'function',
            function: {
              name: 'extract_products',
              description: 'Extrair lista de produtos recomendados do PDF',
              parameters: {
                type: 'object',
                properties: {
                  products: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        asset_class: { type: 'string' },
                        asset_subclass: { type: 'string' },
                        product_name: { type: 'string' },
                        percentage: { type: 'number' },
                        expected_return: { type: 'string' },
                        eligibility: { type: 'string' },
                        product_type: { type: 'string' },
                        profile: { type: 'string', enum: ['conservative', 'moderate', 'sophisticated'] }
                      },
                      required: ['asset_class', 'asset_subclass', 'product_name', 'profile']
                    }
                  }
                },
                required: ['products']
              }
            }
          }
        ],
        tool_choice: { type: 'function', function: { name: 'extract_products' } }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI Gateway error:', response.status, errorText);
      
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: 'Rate limit exceeded. Please try again later.' }),
          { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: 'AI credits exhausted. Please add more credits.' }),
          { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      
      throw new Error(`AI Gateway error: ${response.status}`);
    }

    const aiData = await response.json();
    console.log('AI Response received, processing...');

    // Extract products from tool call response
    const toolCall = aiData.choices?.[0]?.message?.tool_calls?.[0];
    if (!toolCall) {
      throw new Error('No tool call response from AI');
    }

    const productsData = JSON.parse(toolCall.function.arguments);
    const products = productsData.products || [];

    console.log(`Extracted ${products.length} products`);

    // Delete existing products for this month_year first
    const { error: deleteError } = await supabase
      .from('recommended_products')
      .delete()
      .eq('month_year', monthYear);

    if (deleteError) {
      console.error('Error deleting old products:', deleteError);
      // Continue anyway, as the products might not exist
    }

    // Insert products with month_year
    const productsToInsert = products.map((p: any) => ({
      month_year: monthYear,
      asset_class: p.asset_class,
      asset_subclass: p.asset_subclass,
      product_name: p.product_name,
      percentage: p.percentage || null,
      expected_return: p.expected_return || null,
      eligibility: p.eligibility || null,
      product_type: p.product_type || null,
      profile: p.profile
    }));

    const { data, error } = await supabase
      .from('recommended_products')
      .insert(productsToInsert)
      .select();

    if (error) {
      console.error('Database error:', error);
      throw error;
    }

    console.log(`Admin ${claimsData.user.email} successfully inserted ${data?.length || 0} products`);

    return new Response(
      JSON.stringify({ 
        success: true, 
        products_count: data?.length || 0,
        products: data
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in parse-allocation-materials:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
