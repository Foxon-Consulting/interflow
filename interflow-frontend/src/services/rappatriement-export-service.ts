import ExcelJS from 'exceljs';
import { Rappatriement, ProduitRappatriement } from '@/model/rappatriement';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Service pour exporter les rappatriements en format XLSX
 */
export class RappatriementExportService {
  
  /**
   * Charge le template Excel depuis le dossier templates
   * @returns Le workbook du template
   */
  private static async loadTemplate(): Promise<ExcelJS.Workbook> {
    try {
      // Charger le template depuis le dossier public/templates
      const response = await fetch('/templates/template.xlsx');
      if (!response.ok) {
        throw new Error(`Erreur lors du chargement du template: ${response.statusText}`);
      }
      
      const arrayBuffer = await response.arrayBuffer();
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.load(arrayBuffer);
      
      return workbook;
    } catch (error) {
      console.error('❌ [EXPORT] Erreur lors du chargement du template:', error);
      throw new Error('Impossible de charger le template Excel');
    }
  }
  
  /**
   * Exporte un rappatriement en fichier XLSX en utilisant le template
   * @param rappatriement - Le rappatriement à exporter
   */
  static async exportToXLSX(rappatriement: Rappatriement): Promise<void> {
    // Charger le template
    const workbook = await this.loadTemplate();
    
    // Récupérer la première feuille du template
    const worksheet = workbook.worksheets[0];
    
    // Remplir les informations générales du rappatriement (selon la structure du template)
    // Ligne 3: Numéro de transfert et Date de dernière MAJ
    const cellC3 = worksheet.getCell('C3');
    if (cellC3.value) {
      cellC3.value = cellC3.value + rappatriement.numero_transfert;
    }
    
    if (rappatriement.date_derniere_maj) {
      const cellL3 = worksheet.getCell('L3');
      if (cellL3.value) {
        cellL3.value = cellL3.value + format(rappatriement.date_derniere_maj, 'dd/MM/yyyy HH:mm', { locale: fr });
      }
    }
    
    // Ligne 4: Responsable de diffusion
    const cellL4 = worksheet.getCell('L4');
    cellL4.value = 'Responsable de diffusion : ' + rappatriement.responsable_diffusion;
    
    // Ligne 5: Dates et Contacts
    if (rappatriement.date_demande) {
      worksheet.getCell('D5').value = format(rappatriement.date_demande, 'dd/MM/yyyy', { locale: fr });
    }
    
    if (rappatriement.date_reception_souhaitee) {
      worksheet.getCell('G5').value = format(rappatriement.date_reception_souhaitee, 'dd/MM/yyyy', { locale: fr });
    }
    
    if (rappatriement.contacts && rappatriement.contacts.trim()) {
      worksheet.getCell('K5').value = rappatriement.contacts;
    }
    
    // Ligne 6-7: Adresses
    worksheet.getCell('D6').value = rappatriement.adresse_destinataire;
    worksheet.getCell('D7').value = rappatriement.adresse_enlevement;
    
    // Remplir les produits (à partir de la ligne 11, selon le template)
    const templateRowNum = 11; // Ligne de référence dans le template
    const templateRow = worksheet.getRow(templateRowNum);
    
    rappatriement.produits.forEach((produit: ProduitRappatriement, index: number) => {
      const rowNum = templateRowNum + index;
      const row = worksheet.getRow(rowNum);
      
      // Si on ajoute des lignes au-delà du template, copier le style de la ligne template
      if (index > 0) {
        // Dupliquer la ligne template avec ses styles
        row.height = templateRow.height;
        
        // Copier le style de chaque cellule
        ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'].forEach((col, colIndex) => {
          const templateCell = templateRow.getCell(colIndex + 1);
          const targetCell = row.getCell(colIndex + 1);
          
          // Copier le style complet
          if (templateCell.style) {
            targetCell.style = { ...templateCell.style };
          }
        });
      }
      
      // Remplir les valeurs
      row.getCell('A').value = produit.prelevement ? 'X' : '';
      row.getCell('B').value = produit.code_prdt;
      row.getCell('C').value = produit.designation_prdt;
      row.getCell('D').value = produit.lot;
      row.getCell('E').value = produit.poids_net;
      row.getCell('F').value = produit.type_emballage;
      row.getCell('G').value = produit.stock_solde ? 'X' : '';
      row.getCell('H').value = produit.nb_contenants;
      row.getCell('I').value = produit.nb_palettes;
      row.getCell('J').value = produit.dimension_palettes;
      row.getCell('K').value = produit.code_onu;
      row.getCell('L').value = produit.grp_emballage;
      row.getCell('M').value = produit.po;
      
      row.commit();
    });
    
    // Générer le nom du fichier
    const fileName = `Rappatriement_${rappatriement.numero_transfert}_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
    
    // Télécharger le fichier avec préservation des styles
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ [EXPORT] Fichier généré: ${fileName}`);
  }
  
  /**
   * Exporte plusieurs rappatriements dans un seul fichier XLSX (feuilles multiples)
   * @param rappatriements - Liste des rappatriements à exporter
   */
  static async exportMultipleToXLSX(rappatriements: Rappatriement[]): Promise<void> {
    if (rappatriements.length === 0) {
      console.warn('⚠️ [EXPORT] Aucun rappatriement à exporter');
      return;
    }
    
    // Si un seul rappatriement, utiliser l'export simple
    if (rappatriements.length === 1) {
      await this.exportToXLSX(rappatriements[0]);
      return;
    }
    
    // TODO: Implémenter l'export multiple avec plusieurs feuilles
    console.log('🚧 [EXPORT] Export multiple non encore implémenté');
  }
}
