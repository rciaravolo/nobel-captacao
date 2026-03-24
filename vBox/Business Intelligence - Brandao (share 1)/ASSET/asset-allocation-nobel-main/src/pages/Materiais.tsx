import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText, Download, Trash2, Folder, FolderOpen } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { MobileMenu } from '@/components/MobileMenu';
import { PullToRefresh } from '@/components/PullToRefresh';
import nobelLogo from '@/assets/nobel-logo.png';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
interface Material {
  id: string;
  name: string;
  size: string;
  uploadDate: string;
  file?: File;
  url?: string;
  isPreloaded?: boolean;
  folderId?: string;
}
interface MaterialFolder {
  id: string;
  name: string; // Format: "MM/AAAA"
}
const Materiais = () => {
  // Default folders (most recent first)
  const defaultFolders: MaterialFolder[] = [{
    id: 'folder-6',
    name: '03/2026'
  }, {
    id: 'folder-5',
    name: '01/2026'
  }, {
    id: 'folder-4',
    name: '12/2025'
  }, {
    id: 'folder-3',
    name: '11/2025'
  }, {
    id: 'folder-2',
    name: '10/2025'
  }, {
    id: 'folder-1',
    name: '09/2025'
  }];

  // Pre-loaded materials from the uploads
  const preloadedMaterials: Material[] = [{
    id: 'preloaded-12',
    name: 'Produtos-Destaque-Marco-2026.pdf',
    size: '10,4 MB',
    uploadDate: '24/03/2026',
    url: '/materiais/Produtos-Destaque-Marco-2026.pdf',
    isPreloaded: true,
    folderId: 'folder-6'
  }, {
    id: 'preloaded-1',
    name: 'Produtos-Destaque-Setembro-2025.pdf',
    size: '2.8 MB',
    uploadDate: '16/09/2024',
    url: '/materiais/Produtos-Destaque-Setembro-2025.pdf',
    isPreloaded: true,
    folderId: 'folder-1'
  }, {
    id: 'preloaded-2',
    name: 'XP-Alocacao-RMA_setembro25.pdf',
    size: '1.5 MB',
    uploadDate: '16/09/2024',
    url: '/materiais/XP-Alocacao-RMA_setembro25.pdf',
    isPreloaded: true,
    folderId: 'folder-1'
  }, {
    id: 'preloaded-3',
    name: 'Produtos-Destaque-Outubro-2025.pdf',
    size: '2.5 MB',
    uploadDate: '02/01/2025',
    url: '/materiais/Produtos-Destaque-Outubro-2025.pdf',
    isPreloaded: true,
    folderId: 'folder-2'
  }, {
    id: 'preloaded-4',
    name: 'XP-Macro-Mensal-Out25.pdf',
    size: '1.8 MB',
    uploadDate: '02/01/2025',
    url: '/materiais/XP-Macro-Mensal-Out25.pdf',
    isPreloaded: true,
    folderId: 'folder-2'
  }, {
    id: 'preloaded-5',
    name: 'XP-Alocacao-RMA-outubro25.pdf',
    size: '1.6 MB',
    uploadDate: '02/01/2025',
    url: '/materiais/XP-Alocacao-RMA-outubro25.pdf',
    isPreloaded: true,
    folderId: 'folder-2'
  }, {
    id: 'preloaded-6',
    name: 'Produtos-Destaque-Novembro-2025.pdf',
    size: '2.3 MB',
    uploadDate: '02/01/2025',
    url: '/materiais/Produtos-Destaque-Novembro-2025.pdf',
    isPreloaded: true,
    folderId: 'folder-3'
  }, {
    id: 'preloaded-7',
    name: 'XP-Alocacao-RMA-novembro25.pdf',
    size: '1.7 MB',
    uploadDate: '02/01/2025',
    url: '/materiais/XP-Alocacao-RMA-novembro25.pdf',
    isPreloaded: true,
    folderId: 'folder-3'
  }, {
    id: 'preloaded-8',
    name: 'Produtos-Destaque-Dezembro-2025.pdf',
    size: '2.4 MB',
    uploadDate: '09/12/2025',
    url: '/materiais/Produtos-Destaque-Dezembro-2025.pdf',
    isPreloaded: true,
    folderId: 'folder-4'
  }, {
    id: 'preloaded-9',
    name: 'XP-Alocacao-RMA-dezembro25.pdf',
    size: '1.6 MB',
    uploadDate: '09/12/2025',
    url: '/materiais/XP-Alocacao-RMA-dezembro25.pdf',
    isPreloaded: true,
    folderId: 'folder-4'
  }, {
    id: 'preloaded-10',
    name: 'Produtos-Destaque-Janeiro-2026.pdf',
    size: '2.5 MB',
    uploadDate: '14/01/2026',
    url: '/materiais/Produtos-Destaque-Janeiro-2026.pdf',
    isPreloaded: true,
    folderId: 'folder-5'
  }, {
    id: 'preloaded-11',
    name: 'XP-Alocacao-RMA-janeiro26.pdf',
    size: '1.7 MB',
    uploadDate: '14/01/2026',
    url: '/materiais/XP-Alocacao-RMA-janeiro26.pdf',
    isPreloaded: true,
    folderId: 'folder-5'
  }];
  const [folders] = useState<MaterialFolder[]>(defaultFolders);
  const [materials, setMaterials] = useState<Material[]>(preloadedMaterials);
  const [openFolders, setOpenFolders] = useState<Set<string>>(new Set(['folder-1', 'folder-2', 'folder-3', 'folder-4', 'folder-5', 'folder-6']));
  const {
    toast
  } = useToast();
  const handleRefresh = useCallback(async () => {
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Reset materials to preloaded (in a real app, you'd fetch from API)
    setMaterials(preloadedMaterials);
    toast({
      title: "Lista atualizada",
      description: "Os materiais foram recarregados com sucesso."
    });
  }, [toast]);
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;
    Array.from(files).forEach(file => {
      // Check if file is PDF
      if (file.type !== 'application/pdf') {
        toast({
          title: "Formato não suportado",
          description: "Por favor, faça upload apenas de arquivos PDF.",
          variant: "destructive"
        });
        return;
      }
      const newMaterial: Material = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
        uploadDate: new Date().toLocaleDateString('pt-BR'),
        file: file
      };
      setMaterials(prev => [...prev, newMaterial]);
    });
    toast({
      title: "Upload concluído",
      description: `${files.length} arquivo(s) carregado(s) com sucesso.`
    });

    // Reset input
    event.target.value = '';
  };
  const handleDownload = (material: Material) => {
    if (material.isPreloaded && material.url) {
      // For preloaded materials, download from public URL
      const a = document.createElement('a');
      a.href = material.url;
      a.download = material.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } else if (material.file) {
      // For uploaded files, create blob URL
      const url = URL.createObjectURL(material.file);
      const a = document.createElement('a');
      a.href = url;
      a.download = material.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };
  const handleDelete = (id: string) => {
    const material = materials.find(m => m.id === id);
    if (material?.isPreloaded) {
      toast({
        title: "Não é possível remover",
        description: "Este material é padrão do sistema e não pode ser removido.",
        variant: "destructive"
      });
      return;
    }
    setMaterials(prev => prev.filter(material => material.id !== id));
    toast({
      title: "Material removido",
      description: "O material foi removido com sucesso."
    });
  };
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  const toggleFolder = (folderId: string) => {
    setOpenFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(folderId)) {
        newSet.delete(folderId);
      } else {
        newSet.add(folderId);
      }
      return newSet;
    });
  };
  const getMaterialsByFolder = (folderId: string) => {
    return materials.filter(m => m.folderId === folderId);
  };
  return <PullToRefresh onRefresh={handleRefresh}>
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Mobile Layout */}
          <div className="flex items-center justify-between md:hidden">
            <MobileMenu />
            <div className="text-center flex-1">
              <h1 className="text-lg font-bold text-foreground">Materiais</h1>
            </div>
            <img src={nobelLogo} alt="Nobel Capital" className="h-8 w-auto" />
          </div>

          {/* Desktop Layout */}
          <div className="hidden md:grid grid-cols-3 items-center">
            {/* Logo - Left */}
            <div className="flex items-center gap-4">
              <img src={nobelLogo} alt="Nobel Capital" className="h-12 w-auto" />
            </div>
            
            {/* Title - Center */}
            <div className="text-center">
              <h1 className="text-2xl font-bold text-foreground">Materiais</h1>
              <p className="text-sm text-muted-foreground">
                Documentos e recursos de asset allocation
              </p>
            </div>
            
            {/* Button - Right */}
            <div className="flex justify-end">
              <Link to="/">
                <Button variant="outline" className="gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Voltar
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Materials List by Folder */}
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <FileText className="w-6 h-6 text-primary" />
              Materiais por Pasta
            </CardTitle>
          </CardHeader>
          <CardContent>
            {folders.length === 0 ? <div className="text-center py-12">
                <Folder className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2 text-muted-foreground">
                  Nenhuma pasta criada
                </h3>
                <p className="text-muted-foreground">
                  Crie pastas para organizar seus materiais por período.
                </p>
              </div> : <div className="space-y-4">
                {folders.map(folder => {
                const folderMaterials = getMaterialsByFolder(folder.id);
                const isOpen = openFolders.has(folder.id);
                return <Collapsible key={folder.id} open={isOpen} onOpenChange={() => toggleFolder(folder.id)}>
                      <CollapsibleTrigger className="w-full">
                        <div className="flex items-center gap-3 p-4 bg-muted/40 hover:bg-muted/60 rounded-lg transition-colors cursor-pointer">
                          {isOpen ? <FolderOpen className="w-5 h-5 text-primary" /> : <Folder className="w-5 h-5 text-primary" />}
                          <span className="font-semibold text-lg">{folder.name}</span>
                          <span className="text-sm text-muted-foreground ml-auto">
                            {folderMaterials.length} {folderMaterials.length === 1 ? 'material' : 'materiais'}
                          </span>
                        </div>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <div className="mt-2 border rounded-lg overflow-hidden">
                          {folderMaterials.length === 0 ? <div className="text-center py-8 text-muted-foreground">
                              Nenhum material nesta pasta
                            </div> : <>
                              {/* Desktop Table View */}
                              <div className="hidden md:block">
                                <div className="grid grid-cols-5 gap-4 text-sm font-medium text-muted-foreground bg-muted/30 px-4 py-3">
                                  <span>NOME DO ARQUIVO</span>
                                  <span>TAMANHO</span>
                                  <span>DATA DE UPLOAD</span>
                                  <span>TIPO</span>
                                  <span className="text-center">AÇÕES</span>
                                </div>
                                
                                {folderMaterials.map(material => <div key={material.id} className="grid grid-cols-5 gap-4 px-4 py-3 border-t border-border/50 hover:bg-muted/20 transition-colors items-center">
                                    <div className="flex items-center gap-2">
                                      <FileText className="w-4 h-4 text-red-500" />
                                      <span className="font-medium text-foreground truncate">
                                        {material.name}
                                      </span>
                                    </div>
                                    <span className="text-muted-foreground text-sm">
                                      {material.size}
                                    </span>
                                    <span className="text-muted-foreground text-sm">
                                      {material.uploadDate}
                                    </span>
                                    <span className="text-red-500 text-sm font-medium">
                                      PDF
                                    </span>
                                    <div className="flex justify-center gap-2">
                                      <Button variant="outline" size="sm" onClick={() => handleDownload(material)} className="gap-1">
                                        <Download className="w-3 h-3" />
                                        Download
                                      </Button>
                                      {!material.isPreloaded && <Button variant="outline" size="sm" onClick={() => handleDelete(material.id)} className="gap-1 text-destructive hover:text-destructive">
                                          <Trash2 className="w-3 h-3" />
                                          Remover
                                        </Button>}
                                    </div>
                                  </div>)}
                              </div>

                              {/* Mobile Card View */}
                              <div className="md:hidden divide-y divide-border">
                                {folderMaterials.map(material => <div key={material.id} className="p-4 space-y-3">
                                    <div className="flex items-start gap-3">
                                      <div className="p-2 bg-red-50 dark:bg-red-950/30 rounded-lg shrink-0">
                                        <FileText className="w-5 h-5 text-red-500" />
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <p className="font-medium text-foreground text-sm leading-tight break-words">
                                          {material.name}
                                        </p>
                                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                          <span>{material.size}</span>
                                          <span>•</span>
                                          <span>{material.uploadDate}</span>
                                        </div>
                                      </div>
                                    </div>
                                    <div className="flex gap-2">
                                      <Button variant="outline" size="sm" onClick={() => handleDownload(material)} className="flex-1 gap-1.5 text-xs h-9">
                                        <Download className="w-3.5 h-3.5" />
                                        Download
                                      </Button>
                                      {!material.isPreloaded && <Button variant="outline" size="sm" onClick={() => handleDelete(material.id)} className="gap-1.5 text-xs h-9 text-destructive hover:text-destructive">
                                          <Trash2 className="w-3.5 h-3.5" />
                                        </Button>}
                                    </div>
                                  </div>)}
                              </div>
                            </>}
                        </div>
                      </CollapsibleContent>
                    </Collapsible>;
              })}
              </div>}
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>© 2024 Portfolio Advisor. Ferramenta para alocação e projeção de carteiras.</p>
            <p>Desenvolvido com Rafael Brandão - Dados & Performance</p>
          </div>
        </div>
      </footer>
    </div>
  </PullToRefresh>;
};
export default Materiais;