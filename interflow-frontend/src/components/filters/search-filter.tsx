"use client";

import { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, Filter, RotateCcw } from "lucide-react";

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterConfig {
  key: string;
  label: string;
  options: FilterOption[];
  placeholder?: string;
}

export interface SearchFilterProps {
  // Recherche textuelle
  searchValue: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder?: string;
  
  // Filtres par select
  filters?: FilterConfig[];
  filterValues?: Record<string, string>;
  onFilterChange?: (filterKey: string, value: string) => void;
  
  // Actions
  onRefresh?: () => void;
  onReset?: () => void;
  
  // Résultats
  resultCount?: number;
  resultLabel?: string;
  
  // Apparence
  title?: string;
  className?: string;
  children?: ReactNode;
  
  // Statut de chargement
  isLoading?: boolean;
}

export function SearchFilter({
  searchValue,
  onSearchChange,
  searchPlaceholder = "Rechercher...",
  filters = [],
  filterValues = {},
  onFilterChange,
  onRefresh,
  onReset,
  resultCount,
  resultLabel = "résultat(s) trouvé(s)",
  title = "Filtres et Recherche",
  className = "",
  children,
  isLoading = false
}: SearchFilterProps) {
  
  const handleReset = () => {
    onSearchChange("");
    if (onFilterChange && filters) {
      filters.forEach(filter => {
        onFilterChange(filter.key, "tous");
      });
    }
    onReset?.();
  };

  return (
    <Card className={`mb-6 ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
          {/* Champ de recherche */}
          <div className="md:col-span-4">
            <Label htmlFor="recherche">Recherche</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                id="recherche"
                placeholder={searchPlaceholder}
                value={searchValue}
                onChange={(e) => onSearchChange(e.target.value)}
                className="pl-10"
                disabled={isLoading}
              />
            </div>
          </div>
          
          {/* Filtres configurables */}
          {filters.map((filter) => (
            <div key={filter.key} className="md:col-span-2">
              <Label htmlFor={filter.key}>{filter.label}</Label>
              <Select 
                value={filterValues[filter.key] || "tous"} 
                onValueChange={(value) => onFilterChange?.(filter.key, value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={filter.placeholder || "Tous"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tous">Tous</SelectItem>
                  {filter.options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ))}
          
          {/* Contrôles et compteur */}
          <div className="md:col-span-4 flex items-center justify-between gap-2">
            <div className="text-sm text-muted-foreground">
              {resultCount !== undefined && `${resultCount} ${resultLabel}`}
            </div>
            
            <div className="flex gap-2">
              <Button 
                variant="outline"
                size="sm"
                onClick={handleReset}
                disabled={isLoading}
                className="px-3 py-1 text-xs"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Reset
              </Button>
              
              {onRefresh && (
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={onRefresh}
                  disabled={isLoading}
                  className="px-3 py-1 text-xs bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
                >
                  Recharger
                </Button>
              )}
            </div>
          </div>
        </div>
        
        {/* Contenu additionnel */}
        {children}
      </CardContent>
    </Card>
  );
} 