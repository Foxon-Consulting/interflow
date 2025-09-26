import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { BarChart3, ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { useState, useMemo } from "react";

export type DataRow = Record<string, unknown>; // Permet des types plus flexibles

export type SortDirection = "asc" | "desc" | null;

interface DataTableColumn {
  key: string;
  label: string;
  align?: "left" | "center" | "right";
  render?: (value: unknown, row: DataRow) => React.ReactNode;
  sortable?: boolean; // Nouvelle propriété pour indiquer si la colonne est triable
  sortType?: "string" | "number" | "date"; // Type de tri pour optimiser la comparaison
  sortKey?: string; // Clé alternative pour le tri (ex: utiliser 'echeance_sort' pour trier 'echeance')
  secondarySortKey?: string; // Clé de tri secondaire (ex: trier par échéance après code_mp)
  secondarySortType?: "string" | "number" | "date"; // Type de tri secondaire
  secondarySortDirection?: "asc" | "desc"; // Direction du tri secondaire
}

interface DataTableProps {
  caption?: string;
  columns: DataTableColumn[];
  data: DataRow[];
  // Props pour le bouton analyse
  showAnalysisButton?: boolean;
  onAnalysisClick?: () => void;
  isAnalysisLoading?: boolean;
  analysisButtonLabel?: string;
  // Props pour le tri
  defaultSortColumn?: string;
  defaultSortDirection?: SortDirection;
}

export function DataTable({ 
  caption, 
  columns, 
  data, 
  showAnalysisButton = false,
  onAnalysisClick,
  isAnalysisLoading = false,
  analysisButtonLabel = "Lancer l'analyse",
  defaultSortColumn,
  defaultSortDirection = "asc"
}: DataTableProps) {
  
  // État pour le tri
  const [sortColumn, setSortColumn] = useState<string | null>(defaultSortColumn || null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(defaultSortDirection);

  // Fonction pour gérer le clic sur une colonne triable
  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      // Si on clique sur la même colonne, changer la direction
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else if (sortDirection === "desc") {
        setSortDirection(null);
        setSortColumn(null);
      } else {
        setSortDirection("asc");
      }
    } else {
      // Si on clique sur une nouvelle colonne
      setSortColumn(columnKey);
      setSortDirection("asc");
    }
  };

  // Fonction de comparaison pour le tri
  const compareValues = (a: unknown, b: unknown, sortType: string = "string"): number => {
    // Gérer les valeurs nulles/undefined
    if (a == null && b == null) return 0;
    if (a == null) return 1;
    if (b == null) return -1;

    switch (sortType) {
      case "number":
        const numA = typeof a === "number" ? a : parseFloat(String(a));
        const numB = typeof b === "number" ? b : parseFloat(String(b));
        return numA - numB;
      
      case "date":
        const dateA = a instanceof Date ? a : new Date(String(a));
        const dateB = b instanceof Date ? b : new Date(String(b));
        return dateA.getTime() - dateB.getTime();
      
      case "string":
      default:
        return String(a).localeCompare(String(b), 'fr', { 
          numeric: true, 
          sensitivity: 'base' 
        });
    }
  };

  // Données triées
  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) {
      return data;
    }

    const column = columns.find(col => col.key === sortColumn);
    const sortType = column?.sortType || "string";

    return [...data].sort((a, b) => {
      const sortKey = column?.sortKey || sortColumn;
      const valueA = a[sortKey];
      const valueB = b[sortKey];
      
      // Tri principal
      const comparison = compareValues(valueA, valueB, sortType);
      const primaryResult = sortDirection === "asc" ? comparison : -comparison;
      
      // Si les valeurs sont égales et qu'il y a un tri secondaire
      if (primaryResult === 0 && column?.secondarySortKey) {
        const secondaryValueA = a[column.secondarySortKey];
        const secondaryValueB = b[column.secondarySortKey];
        const secondaryType = column.secondarySortType || "string";
        const secondaryComparison = compareValues(secondaryValueA, secondaryValueB, secondaryType);
        
        // Appliquer la direction du tri secondaire (par défaut "asc")
        const secondaryDirection = column.secondarySortDirection || "asc";
        return secondaryDirection === "asc" ? secondaryComparison : -secondaryComparison;
      }
      
      return primaryResult;
    });
  }, [data, sortColumn, sortDirection, columns]);

  // Fonction pour rendre l'icône de tri
  const renderSortIcon = (columnKey: string) => {
    if (sortColumn !== columnKey) {
      return <ChevronsUpDown size={14} className="text-gray-400" />;
    }
    
    if (sortDirection === "asc") {
      return <ChevronUp size={14} className="text-blue-600" />;
    } else if (sortDirection === "desc") {
      return <ChevronDown size={14} className="text-blue-600" />;
    }
    
    return <ChevronsUpDown size={14} className="text-gray-400" />;
  };

  return (
    <div className="space-y-4">
      {/* Bouton d'analyse si activé */}
      {showAnalysisButton && (
        <div className="flex justify-end">
          <Button
            onClick={onAnalysisClick}
            disabled={isAnalysisLoading}
            className="flex items-center gap-2"
            variant="outline"
          >
            {isAnalysisLoading ? (
              <>
                <LoadingSpinner size={16} />
                Analyse en cours...
              </>
            ) : (
              <>
                <BarChart3 size={16} />
                {analysisButtonLabel}
              </>
            )}
          </Button>
        </div>
      )}

      {/* Table */}
      <Table>
        {caption && <TableCaption>{caption}</TableCaption>}
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead 
                key={column.key} 
                className={`${column.align === "right" ? "text-right" : column.align === "center" ? "text-center" : ""} ${
                  column.sortable ? "cursor-pointer hover:bg-gray-50 select-none" : ""
                }`}
                onClick={column.sortable ? () => handleSort(column.key) : undefined}
              >
                <div className={`flex items-center gap-1 ${
                  column.align === "right" ? "justify-end" : 
                  column.align === "center" ? "justify-center" : ""
                }`}>
                  <span>{column.label}</span>
                  {column.sortable && renderSortIcon(column.key)}
                </div>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedData.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns.map((column) => {
                const value = row[column.key];
                
                return (
                  <TableCell
                    key={`${rowIndex}-${column.key}`}
                    className={column.align === "right" ? "text-right" : column.align === "center" ? "text-center" : ""}
                  >
                    {column.render ? column.render(value, row) : String(value ?? '')}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
} 