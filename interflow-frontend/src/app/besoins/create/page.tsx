"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Etat } from "@/model/besoin";
import { MatiereModel } from "@/model/matiere";
import { fetchMatiereByCode } from "@/services/matiere-service";
import { createBesoin } from "@/services/besoin-service";
import { AnalyseService } from "@/services/analyse-service";
import { Save, ArrowLeft, AlertCircle, Search, Calculator } from "lucide-react";
import { format } from "date-fns";

interface FormData {
  // Champs pour le besoin
  code_mp: string;
  quantite: string;
  echeance: string;
  lot: string;
}

export default function CreateBesoinPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isSearchingMatiere, setIsSearchingMatiere] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState(false);
  const [foundMatiere, setFoundMatiere] = useState<MatiereModel | null>(null);
  const [matiereError, setMatiereError] = useState<string>("");
  const [calculatedEtat, setCalculatedEtat] = useState<Etat | null>(null);
  const [analyseError, setAnalyseError] = useState<string>("");

  const [formData, setFormData] = useState<FormData>({
    code_mp: "",
    quantite: "",
    echeance: format(new Date(), "yyyy-MM-dd"),
    lot: ""
  });

  const [errors, setErrors] = useState<Partial<FormData>>({});

  // Fonction pour rechercher une matière par code MP
  const searchMatiereByCode = async (code_mp: string) => {
    if (!code_mp.trim()) {
      setFoundMatiere(null);
      setMatiereError("");
      setCalculatedEtat(null);
      return;
    }

    setIsSearchingMatiere(true);
    setMatiereError("");

    try {
      const matiere = await fetchMatiereByCode(code_mp.trim());
      
      if (matiere) {
        setFoundMatiere(matiere);
        setMatiereError("");
      } else {
        setFoundMatiere(null);
        setMatiereError(`Aucune matière trouvée pour le code "${code_mp}"`);
        setCalculatedEtat(null);
      }
    } catch (err) {
      console.error("Erreur lors de la recherche de matière:", err);
      setFoundMatiere(null);
      setMatiereError("Erreur lors de la recherche de la matière");
      setCalculatedEtat(null);
    } finally {
      setIsSearchingMatiere(false);
    }
  };

  // Fonction pour calculer l'état du besoin via l'analyse
  const calculateBesoinEtat = async (code_mp: string, quantite: number, echeance: string) => {
    if (!code_mp.trim() || !quantite || !echeance) {
      setCalculatedEtat(null);
      return;
    }

    setIsAnalyzing(true);
    setAnalyseError("");

    try {
      // Calculer l'analyse avec un horizon de 30 jours pour avoir une vue d'ensemble
      const analyseResult = await AnalyseService.calculerQuantites(code_mp.trim(), 30, echeance);
      
      if (analyseResult.couverture_par_besoin && analyseResult.couverture_par_besoin.length > 0) {
        // Rechercher la couverture pour notre besoin spécifique
        const echeanceDate = new Date(echeance).toISOString().split('T')[0];
        
        const besoinCouverture = analyseResult.couverture_par_besoin.find(c => {
          const couvertureDate = c.echeance.split('T')[0];
          const quantiteMatch = Math.abs(c.quantite - quantite) < 0.01;
          return couvertureDate === echeanceDate && quantiteMatch;
        });

        if (besoinCouverture) {
          // Mapper l'état de l'analyse vers notre enum
          let etat: Etat;
          switch (besoinCouverture.etat_couverture.toLowerCase()) {
            case 'couvert':
              etat = Etat.COUVERT;
              break;
            case 'partiel':
              etat = Etat.PARTIEL;
              break;
            case 'non_couvert':
              etat = Etat.NON_COUVERT;
              break;
            default:
              etat = Etat.INCONNU;
          }
          setCalculatedEtat(etat);
        } else {
          // Si pas de couverture spécifique trouvée, analyser la situation globale
          if (analyseResult.stock_manquant && analyseResult.stock_manquant > 0) {
            setCalculatedEtat(Etat.NON_COUVERT);
          } else if (analyseResult.taux_couverture && analyseResult.taux_couverture < 100) {
            setCalculatedEtat(Etat.PARTIEL);
          } else {
            setCalculatedEtat(Etat.COUVERT);
          }
        }
      } else {
        // Si aucune donnée d'analyse, considérer comme INCONNU
        setCalculatedEtat(Etat.INCONNU);
      }
    } catch (err) {
      console.error("Erreur lors du calcul de l'état:", err);
      setAnalyseError("Impossible de calculer l'état du besoin");
      // En cas d'erreur, état par défaut
      setCalculatedEtat(Etat.INCONNU);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Effet pour rechercher la matière quand le code MP change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (formData.code_mp) {
        searchMatiereByCode(formData.code_mp);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [formData.code_mp]);

  // Effet pour calculer l'état quand les paramètres du besoin changent
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (foundMatiere && formData.quantite && formData.echeance) {
        const quantite = parseFloat(formData.quantite);
        if (!isNaN(quantite) && quantite > 0) {
          calculateBesoinEtat(formData.code_mp, quantite, formData.echeance);
        }
      }
    }, 1000); // Délai plus long pour l'analyse

    return () => clearTimeout(timeoutId);
  }, [foundMatiere, formData.quantite, formData.echeance, formData.code_mp]);

  // Fonction de validation
  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {};

    if (!formData.code_mp.trim()) {
      newErrors.code_mp = "Le code MP est obligatoire";
    }

    // Suppression du verrou : on n'exige plus que la matière soit trouvée dans les références

    if (!formData.quantite.trim()) {
      newErrors.quantite = "La quantité est obligatoire";
    } else {
      const quantite = parseFloat(formData.quantite);
      if (isNaN(quantite) || quantite <= 0) {
        newErrors.quantite = "La quantité doit être un nombre positif";
      }
    }

    if (!formData.echeance) {
      newErrors.echeance = "L'échéance est obligatoire";
    }
    // Suppression de la validation : les échéances dans le passé sont maintenant autorisées

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Fonction pour gérer les changements de champs
  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Effacer l'erreur du champ modifié
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  // Fonction pour sauvegarder le besoin
  const handleSave = async () => {
    setError("");
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Préparer les données du besoin pour l'API
      let matiereData;
      
      if (foundMatiere) {
        // Utiliser la matière trouvée dans les références
        matiereData = foundMatiere;
      } else {
        // Créer une matière minimale avec le code MP saisi
        matiereData = {
          code_mp: formData.code_mp.trim(),
          nom: formData.code_mp.trim(), // Utiliser le code comme nom par défaut
          description: null,
          fds: null,
          seveso: null,
          internal_reference: null
        };
      }

      const besoinData = {
        matiere: matiereData,
        quantite: parseFloat(formData.quantite),
        echeance: new Date(formData.echeance),
        etat: calculatedEtat || Etat.INCONNU, // Utiliser l'état calculé ou INCONNU par défaut
        lot: formData.lot.trim()
      };

      console.log("📡 Création du besoin via API...", besoinData);
      
      // Appel API pour créer le besoin
      const createdBesoin = await createBesoin(besoinData);
      
      console.log("✅ Besoin créé avec succès:", createdBesoin);
      
      setSuccess(true);
      
      // Rediriger vers la liste des besoins après un délai
      setTimeout(() => {
        router.push("/besoins");
      }, 2000);

    } catch (err) {
      console.error("❌ Erreur lors de la création du besoin:", err);
      setError(err instanceof Error ? err.message : "Une erreur est survenue lors de la création du besoin");
    } finally {
      setIsLoading(false);
    }
  };

  // Fonction pour annuler et retourner à la liste
  const handleCancel = () => {
    router.push("/besoins");
  };

  // Fonction pour obtenir le libellé et la couleur de l'état
  const getEtatDisplay = (etat: Etat | null) => {
    if (!etat) return { label: "En cours de calcul...", color: "bg-gray-100 text-gray-800" };
    
    switch (etat) {
      case Etat.COUVERT:
        return { label: "Couvert", color: "bg-green-100 text-green-800" };
      case Etat.PARTIEL:
        return { label: "Partiellement couvert", color: "bg-yellow-100 text-yellow-800" };
      case Etat.NON_COUVERT:
        return { label: "Non couvert", color: "bg-red-100 text-red-800" };
      case Etat.INCONNU:
      default:
        return { label: "INCONNU", color: "bg-blue-100 text-blue-800" };
    }
  };

  if (success) {
    return (
      <div className="container py-10">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-2xl font-semibold text-green-700 mb-2">Besoin créé avec succès !</h2>
              <p className="text-gray-600">Redirection vers la liste des besoins...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-10">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <div className="flex items-center gap-4 mb-6">
          <Button variant="outline" onClick={handleCancel}>
            <ArrowLeft size={16} />
            Retour
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Créer un nouveau besoin</h1>
            <p className="text-gray-600">Ajoutez un nouveau besoin opérationnel - l&apos;état sera calculé automatiquement. La matière peut être créée si elle n&apos;existe pas. Les échéances passées sont autorisées.</p>
          </div>
        </div>

        {/* Messages d'erreur globaux */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Section Matière (recherche par code) */}
          <Card>
            <CardHeader>
              <CardTitle>Recherche de matière</CardTitle>
              <CardDescription>Saisissez le code MP - si la matière existe dans les références, ses informations seront récupérées automatiquement</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="code_mp">Code MP *</Label>
                <div className="relative">
                  <Input
                    id="code_mp"
                    value={formData.code_mp}
                    onChange={(e) => handleInputChange("code_mp", e.target.value)}
                    placeholder="Ex: MP001"
                    className={errors.code_mp ? "border-red-500" : ""}
                  />
                  {isSearchingMatiere && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <LoadingSpinner size={16} />
                    </div>
                  )}
                </div>
                {errors.code_mp && (
                  <p className="text-sm text-red-500 mt-1">{errors.code_mp}</p>
                )}
                {matiereError && (
                  <p className="text-sm text-orange-600 mt-1">⚠️ {matiereError}</p>
                )}
              </div>

              {/* Affichage des informations de la matière trouvée */}
              {foundMatiere && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Search className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Matière trouvée dans les références</span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="grid grid-cols-2 gap-2">
                      <span className="font-medium">Code MP:</span>
                      <span>{foundMatiere.code_mp}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <span className="font-medium">Nom:</span>
                      <span>{foundMatiere.nom}</span>
                    </div>
                    {foundMatiere.description && (
                      <div className="grid grid-cols-2 gap-2">
                        <span className="font-medium">Description:</span>
                        <span className="text-xs">{foundMatiere.description}</span>
                      </div>
                    )}
                    {foundMatiere.seveso && (
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                          ⚠️ Matière Seveso
                        </span>
                      </div>
                    )}
                    {foundMatiere.fds && (
                      <div className="grid grid-cols-2 gap-2">
                        <span className="font-medium">FDS:</span>
                        <span className="text-xs">{foundMatiere.fds}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Affichage quand la matière n'est pas trouvée mais qu'on peut continuer */}
              {matiereError && formData.code_mp.trim() && (
                <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertCircle className="h-4 w-4 text-orange-600" />
                    <span className="text-sm font-medium text-orange-800">Matière non référencée</span>
                  </div>
                  
                  <div className="space-y-2 text-sm text-orange-700">
                    <p>Le code MP &quot;{formData.code_mp}&quot; n&apos;existe pas dans les références.</p>
                    <p>Le besoin sera créé avec les informations minimales :</p>
                    <div className="ml-4 space-y-1">
                      <div className="grid grid-cols-2 gap-2">
                        <span className="font-medium">Code MP:</span>
                        <span>{formData.code_mp}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <span className="font-medium">Nom:</span>
                        <span>{formData.code_mp} (par défaut)</span>
                      </div>
                      <div className="text-xs text-orange-600">
                        💡 Vous pourrez ajouter cette matière aux références plus tard si nécessaire.
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Section Besoin */}
          <Card>
            <CardHeader>
              <CardTitle>Détails du besoin</CardTitle>
              <CardDescription>Informations spécifiques au besoin opérationnel</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="quantite">Quantité *</Label>
                <Input
                  id="quantite"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.quantite}
                  onChange={(e) => handleInputChange("quantite", e.target.value)}
                  placeholder="Ex: 100.5"
                  className={errors.quantite ? "border-red-500" : ""}
                />
                {errors.quantite && (
                  <p className="text-sm text-red-500 mt-1">{errors.quantite}</p>
                )}
              </div>

              <div>
                <Label htmlFor="echeance">Date d&apos;échéance *</Label>
                <Input
                  id="echeance"
                  type="date"
                  value={formData.echeance}
                  onChange={(e) => handleInputChange("echeance", e.target.value)}
                  className={errors.echeance ? "border-red-500" : ""}
                />
                {errors.echeance && (
                  <p className="text-sm text-red-500 mt-1">{errors.echeance}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  💡 Les échéances passées sont autorisées (pour les besoins historiques)
                </p>
              </div>

              <div>
                <Label htmlFor="lot">Numéro de lot</Label>
                <Input
                  id="lot"
                  value={formData.lot}
                  onChange={(e) => handleInputChange("lot", e.target.value)}
                  placeholder="Ex: LOT2024001 (optionnel - besoin général si vide)"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.lot.trim() 
                    ? "🎯 Besoin spécifique pour ce lot" 
                    : "📋 Besoin général (tous lots confondus)"
                  }
                </p>
              </div>

              {/* État calculé automatiquement */}
              <div>
                <Label>État du besoin (calculé automatiquement)</Label>
                <div className="flex items-center gap-2 mt-2">
                  {isAnalyzing && (
                    <div className="flex items-center gap-2">
                      <Calculator className="h-4 w-4 animate-pulse" />
                      <span className="text-sm">Analyse en cours...</span>
                    </div>
                  )}
                  {!isAnalyzing && calculatedEtat && (
                    <span className={`px-2 py-1 rounded text-sm ${getEtatDisplay(calculatedEtat).color}`}>
                      {getEtatDisplay(calculatedEtat).label}
                    </span>
                  )}
                  {analyseError && (
                    <p className="text-sm text-orange-600">⚠️ {analyseError}</p>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  L&apos;état est calculé en temps réel basé sur l&apos;analyse de couverture
                </p>
              </div>

              {/* Aperçu de l&apos;ID généré */}
              {formData.code_mp && formData.echeance && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <Label className="text-sm font-medium">ID qui sera généré :</Label>
                  <p className="text-sm text-gray-600 mt-1">
                    {formData.code_mp}_{formData.echeance.replace(/-/g, '')}
                    {formData.lot && `_${formData.lot}`}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Boutons d'action */}
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={handleCancel} disabled={isLoading}>
            Annuler
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? (
              <>
                <LoadingSpinner size={16} />
                Création en cours...
              </>
            ) : (
              <>
                <Save size={16} />
                Créer le besoin
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
