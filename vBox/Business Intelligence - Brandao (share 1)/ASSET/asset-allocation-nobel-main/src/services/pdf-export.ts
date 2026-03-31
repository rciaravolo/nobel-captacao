import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { AllocationResult } from '@/types/portfolio';
import nobelLogo from '@/assets/nobel-logo.png';
import { RecommendedProduct } from './recommendations';

export class PDFExportService {
  static async exportProposal(
    results: AllocationResult[],
    totalValue: number,
    scenario: string,
    recommendations: RecommendedProduct[]
  ) {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    const contentWidth = pageWidth - (2 * margin);
    
    // Add logo
    try {
      const logoImg = new Image();
      logoImg.src = nobelLogo;
      await new Promise((resolve) => {
        logoImg.onload = resolve;
      });
      
      pdf.addImage(logoImg, 'PNG', margin, 15, 40, 12);
    } catch (error) {
      console.warn('Could not load logo:', error);
    }
    
    // Title
    pdf.setFontSize(18);
    pdf.setTextColor(32, 32, 32);
    pdf.text('Proposta de Alocação de Portfolio', margin, 38);
    
    // Subtitle with scenario info
    pdf.setFontSize(11);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Perfil: ${scenario}`, margin, 47);
    
    // Total value
    pdf.setFontSize(13);
    pdf.setTextColor(32, 32, 32);
    const formattedValue = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(totalValue);
    pdf.text(`Valor Total a Alocar: ${formattedValue}`, margin, 58);
    
    // Table header
    let yPos = 70;
    pdf.setFontSize(11);
    pdf.setTextColor(32, 32, 32);
    pdf.text('Resultados da Alocação:', margin, yPos);
    yPos += 8;
    
    // Table
    pdf.setFontSize(9);
    const tableHeaders = ['Classe', 'Subclasse', 'Valor (R$)', '%'];
    const colWidths = [45, 50, 38, 27];
    let xPos = margin;
    
    // Draw header
    pdf.setTextColor(255, 255, 255);
    pdf.setFillColor(255, 209, 0);
    pdf.rect(xPos, yPos, colWidths.reduce((a, b) => a + b, 0), 7, 'F');
    
    tableHeaders.forEach((header, index) => {
      pdf.text(header, xPos + 2, yPos + 4.5);
      xPos += colWidths[index];
    });
    
    yPos += 7;
    
    // Draw rows
    pdf.setTextColor(32, 32, 32);
    const filteredResults = results.filter(item => item.percentage > 0);
    filteredResults.forEach((item, index) => {
      // Check if we need a new page
      if (yPos > pageHeight - 30) {
        pdf.addPage();
        yPos = 20;
      }
      
      xPos = margin;
      
      // Alternate row colors
      if (index % 2 === 0) {
        pdf.setFillColor(248, 248, 248);
        pdf.rect(xPos, yPos, colWidths.reduce((a, b) => a + b, 0), 5.5, 'F');
      }
      
      const rowData = [
        item.classe,
        item.subclass === '-' ? item.classe : item.subclass,
        new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(item.value),
        `${item.percentage.toFixed(1)}%`
      ];
      
      rowData.forEach((data, colIndex) => {
        pdf.text(data, xPos + 2, yPos + 3.8);
        xPos += colWidths[colIndex];
      });
      
      yPos += 5.5;
    });
    
    // Add chart section
    yPos += 12;
    if (yPos > pageHeight - 90) {
      pdf.addPage();
      yPos = 20;
    }
    
    pdf.setFontSize(11);
    pdf.setTextColor(32, 32, 32);
    pdf.text('Gráfico de Alocação:', margin, yPos);
    yPos += 8;
    
    // Capture chart element and add to PDF
    let chartHeight = 0;
    try {
      const chartElement = document.querySelector('[data-chart-container]') as HTMLElement;
      if (chartElement) {
        const canvas = await html2canvas(chartElement, {
          backgroundColor: '#ffffff',
          scale: 2
        });
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = contentWidth;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        chartHeight = imgHeight;
        
        if (yPos + imgHeight > pageHeight - 25) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.addImage(imgData, 'PNG', margin, yPos, imgWidth, imgHeight);
        yPos += imgHeight + 12;
      }
    } catch (error) {
      console.warn('Could not capture chart:', error);
      pdf.text('Gráfico não pôde ser capturado', margin, yPos);
      yPos += 10;
    }
    
    // Add recommended products section
    if (yPos > pageHeight - 50) {
      pdf.addPage();
      yPos = 20;
    }
    
    pdf.setFontSize(11);
    pdf.setTextColor(32, 32, 32);
    pdf.text('Produtos Recomendados:', margin, yPos);
    yPos += 8;
    
    if (recommendations && recommendations.length > 0) {
      pdf.setFontSize(8);
      pdf.setTextColor(60, 60, 60);
      
      // Group by asset class and subclass
      const groupedProducts = filteredResults.reduce((acc, item) => {
        const key = `${item.classe} - ${item.subclass}`;
        const products = recommendations.filter(
          r => r.asset_class === item.classe && r.asset_subclass === item.subclass
        );
        if (products.length > 0) {
          acc[key] = products;
        }
        return acc;
      }, {} as Record<string, typeof recommendations>);
      
      // Display products by group
      Object.entries(groupedProducts).forEach(([group, products]) => {
        if (yPos > pageHeight - 20) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.setFontSize(9);
        pdf.setTextColor(32, 32, 32);
        pdf.text(group, margin, yPos);
        yPos += 5;
        
        pdf.setFontSize(8);
        pdf.setTextColor(60, 60, 60);
        
        products.forEach((product) => {
          if (yPos > pageHeight - 15) {
            pdf.addPage();
            yPos = 20;
          }
          
          const returnText = product.expected_return ? ` (${product.expected_return})` : '';
          const eligibilityText = product.eligibility ? ` - ${product.eligibility}` : '';
          const text = `• ${product.product_name}${returnText}${eligibilityText}`;
          
          const splitText = pdf.splitTextToSize(text, contentWidth - 5);
          pdf.text(splitText, margin + 3, yPos);
          yPos += splitText.length * 4;
        });
        
        yPos += 3;
      });
    } else {
      pdf.setFontSize(8);
      pdf.setTextColor(100, 100, 100);
      pdf.text('Nenhum produto recomendado disponível para este perfil.', margin, yPos);
    }
    
    // Footer on last page
    const currentDate = new Date().toLocaleDateString('pt-BR');
    pdf.setFontSize(7);
    pdf.setTextColor(120, 120, 120);
    pdf.text(`Documento gerado em ${currentDate}`, margin, pageHeight - 8);
    pdf.text('© 2024 Portfolio Advisor - Nobel Capital', pageWidth - 70, pageHeight - 8);
    
    // Save the PDF
    pdf.save(`proposta-alocacao-${scenario.toLowerCase().replace(/\s+/g, '-')}-${new Date().getTime()}.pdf`);
  }

  static async exportProductsList(
    recommendations: RecommendedProduct[],
    scenario: string
  ) {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    const contentWidth = pageWidth - (2 * margin);
    
    // Add logo
    try {
      const logoImg = new Image();
      logoImg.src = nobelLogo;
      await new Promise((resolve) => {
        logoImg.onload = resolve;
      });
      
      pdf.addImage(logoImg, 'PNG', margin, 15, 40, 12);
    } catch (error) {
      console.warn('Could not load logo:', error);
    }
    
    // Title
    pdf.setFontSize(18);
    pdf.setTextColor(32, 32, 32);
    pdf.text('Produtos Recomendados', margin, 38);
    
    // Subtitle with scenario info
    pdf.setFontSize(11);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Perfil: ${scenario}`, margin, 47);
    
    let yPos = 58;
    
    if (recommendations && recommendations.length > 0) {
      // Group by asset class and subclass
      const groupedProducts = recommendations.reduce((acc, product) => {
        const key = `${product.asset_class} - ${product.asset_subclass}`;
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(product);
        return acc;
      }, {} as Record<string, typeof recommendations>);
      
      // Display products by group
      Object.entries(groupedProducts).forEach(([group, products]) => {
        if (yPos > pageHeight - 30) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setTextColor(32, 32, 32);
        pdf.text(group, margin, yPos);
        yPos += 7;
        
        pdf.setFontSize(9);
        pdf.setTextColor(60, 60, 60);
        
        products.forEach((product) => {
          if (yPos > pageHeight - 20) {
            pdf.addPage();
            yPos = 20;
          }
          
          const returnText = product.expected_return ? ` (${product.expected_return})` : '';
          const eligibilityText = product.eligibility ? ` - ${product.eligibility}` : '';
          const text = `• ${product.product_name}${returnText}${eligibilityText}`;
          
          const splitText = pdf.splitTextToSize(text, contentWidth - 5);
          pdf.text(splitText, margin + 3, yPos);
          yPos += splitText.length * 5;
        });
        
        yPos += 5;
      });
    } else {
      pdf.setFontSize(9);
      pdf.setTextColor(100, 100, 100);
      pdf.text('Nenhum produto recomendado disponível para este perfil.', margin, yPos);
    }
    
    // Footer
    const currentDate = new Date().toLocaleDateString('pt-BR');
    pdf.setFontSize(7);
    pdf.setTextColor(120, 120, 120);
    pdf.text(`Documento gerado em ${currentDate}`, margin, pageHeight - 8);
    pdf.text('© 2024 Portfolio Advisor - Nobel Capital', pageWidth - 70, pageHeight - 8);
    
    // Save the PDF
    pdf.save(`produtos-recomendados-${scenario.toLowerCase().replace(/\s+/g, '-')}-${new Date().getTime()}.pdf`);
  }
}