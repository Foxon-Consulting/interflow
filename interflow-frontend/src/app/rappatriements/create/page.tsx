"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";
import { createRappatriement } from "@/services/rappatriement-service";
import { ProduitRappatriementModel, TypeEmballage } from "@/model/rappatriement";

interface ProduitFormData {
  code_prdt: string;
  designation_prdt: string;
  lot: string;
  poids_net: number;
  type_emballage: TypeEmballage;
  stock_solde: boolean;
  nb_contenants: number;
  nb_palettes: number;
  dimension_palettes: string;
  code_onu: string;
  grp_emballage: string;
  po: string;
}

export default function CreateRappatriementPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isClient, setIsClient] = useState(false);
  
  // État du formulaire principal
  const [formData, setFormData] = useState({
    responsable_diffusion: "Lucas Raybaud",
    date_demande: "",
    date_reception_souhaitee: "",
    contacts: "Aucun contact renseigné",
    adresse_destinataire: "BSL La Sarée - Usine La Sarée, Route de Gourdon, 06620 Le Bar Sur Loup",
    adresse_enlevement: "EXMP - ZONE 10 - Le Pal - 9 chemin de la Ginestiere. 06200, Nice",
    remarques: "Règle du rapatriement à la palette UNIQUEMENT (excepté pour les rubriques 1450,4110 et le stockage froid liés aux aspects règlementaires et capacitaires)."
  });

  // Fonction pour obtenir la date d'aujourd'hui au format YYYY-MM-DD
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Définir les dates côté client uniquement pour éviter les erreurs d'hydratation
  useEffect(() => {
    setIsClient(true);
    
    const today = getTodayDate();
    setFormData(prev => ({
      ...prev,
      date_demande: today,
      date_reception_souhaitee: today
    }));

    // Récupérer les données du stock sélectionné depuis localStorage
    const stockData = localStorage.getItem('rappatriement_stock_data');
    if (stockData) {
      try {
        const parsedStockData = JSON.parse(stockData);
        setCurrentProduit(prev => ({
          ...prev,
          ...parsedStockData
        }));
        setProduitFromStock(true);
        
        // Nettoyer le localStorage après récupération
        localStorage.removeItem('rappatriement_stock_data');
      } catch (error) {
        console.error('Erreur lors du parsing des données du stock:', error);
      }
    }
  }, []);

  // État des produits
  const [produits, setProduits] = useState<ProduitFormData[]>([]);
  const [currentProduit, setCurrentProduit] = useState<ProduitFormData>({
    code_prdt: "",
    designation_prdt: "",
    lot: "",
    poids_net: 0,
    type_emballage: TypeEmballage.CARTON,
    stock_solde: false,
    nb_contenants: 0,
    nb_palettes: 0,
    dimension_palettes: "",
    code_onu: "SANS DANGER",
    grp_emballage: "",
    po: ""
  });
  const [produitFromStock, setProduitFromStock] = useState(false);

  // Gestion des changements du formulaire principal
  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Gestion des changements du produit en cours
  const handleProduitChange = (field: string, value: string | number | boolean) => {
    setCurrentProduit(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Ajouter un produit à la liste
  const handleAddProduit = () => {
    if (!currentProduit.code_prdt || !currentProduit.designation_prdt || !currentProduit.lot) {
      toast({
        title: "Erreur",
        description: "Le code produit, la désignation et le lot sont obligatoires",
        variant: "destructive"
      });
      return;
    }

    setProduits(prev => [...prev, { ...currentProduit }]);
    setCurrentProduit({
      code_prdt: "",
      designation_prdt: "",
      lot: "",
      poids_net: 0,
      type_emballage: TypeEmballage.CARTON,
      stock_solde: false,
      nb_contenants: 0,
      nb_palettes: 0,
      dimension_palettes: "",
      code_onu: "SANS DANGER",
      grp_emballage: "",
      po: ""
    });
  };

  // Supprimer un produit de la liste
  const handleRemoveProduit = (index: number) => {
    setProduits(prev => prev.filter((_, i) => i !== index));
  };

  // Validation du formulaire
  const validateForm = (): boolean => {
    if (!formData.responsable_diffusion.trim()) {
      toast({
        title: "Erreur",
        description: "Le responsable de diffusion est obligatoire",
        variant: "destructive"
      });
      return false;
    }

    if (!formData.adresse_destinataire.trim()) {
      toast({
        title: "Erreur",
        description: "L'adresse destinataire est obligatoire",
        variant: "destructive"
      });
      return false;
    }

    if (!formData.adresse_enlevement.trim()) {
      toast({
        title: "Erreur",
        description: "L'adresse d'enlèvement est obligatoire",
        variant: "destructive"
      });
      return false;
    }

    if (produits.length === 0) {
      toast({
        title: "Erreur",
        description: "Au moins un produit doit être ajouté",
        variant: "destructive"
      });
      return false;
    }

    return true;
  };

  // Soumission du formulaire
  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      // Convertir les produits en ProduitRappatriementModel
      const produitsModels = produits.map(produit => new ProduitRappatriementModel({
        ...produit,
        prelevement: false // Par défaut, le produit n'est pas prélevé
      }));

      // Créer l'objet rapatriement
      const nouveauRappatriement = {
        responsable_diffusion: formData.responsable_diffusion,
        date_demande: formData.date_demande ? new Date(formData.date_demande) : null,
        date_reception_souhaitee: formData.date_reception_souhaitee ? new Date(formData.date_reception_souhaitee) : null,
        contacts: formData.contacts,
        adresse_destinataire: formData.adresse_destinataire,
        adresse_enlevement: formData.adresse_enlevement,
        produits: produitsModels,
        remarques: formData.remarques || null
      };

      // Log du JSON envoyé au backend
      console.log("🔍 [CREATE-RAPPATRIEMENT] JSON envoyé au backend:", JSON.stringify(nouveauRappatriement, null, 2));

      // Appeler le service de création
      const rapatriementCree = await createRappatriement(nouveauRappatriement);

      toast({
        title: "Succès",
        description: `Rapatriement créé avec succès (${rapatriementCree.numero_transfert})`,
      });

      // Rediriger vers la liste des rapatriements
      router.push("/rappatriements");

    } catch (error) {
      console.error("Erreur lors de la création du rapatriement:", error);
      toast({
        title: "Erreur",
        description: "Erreur lors de la création du rapatriement",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Ne rendre le contenu que côté client pour éviter les erreurs d'hydratation
  if (!isClient) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <div className="flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-3xl font-bold">Chargement...</h1>
            <p className="text-muted-foreground">Préparation du formulaire</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Créer un rapatriement</h1>
          <p className="text-muted-foreground">
            Remplissez le formulaire ci-dessous pour créer un nouveau rapatriement
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => router.push("/rappatriements")}
        >
          Retour à la liste
        </Button>
      </div>

      <div className="grid gap-6">
        {/* Informations générales */}
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
            <CardDescription>
              Informations de base sur le rapatriement
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="responsable_diffusion">Responsable de diffusion *</Label>
                <Input
                  id="responsable_diffusion"
                  value={formData.responsable_diffusion}
                  onChange={(e) => handleFormChange("responsable_diffusion", e.target.value)}
                  placeholder="Nom du responsable"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contacts">Contacts</Label>
                <Input
                  id="contacts"
                  value={formData.contacts}
                  onChange={(e) => handleFormChange("contacts", e.target.value)}
                  placeholder="Téléphone, email..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="date_demande">Date de demande</Label>
                <Input
                  id="date_demande"
                  type="date"
                  value={formData.date_demande}
                  onChange={(e) => handleFormChange("date_demande", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="date_reception_souhaitee">Date de réception souhaitée</Label>
                <Input
                  id="date_reception_souhaitee"
                  type="date"
                  value={formData.date_reception_souhaitee}
                  onChange={(e) => handleFormChange("date_reception_souhaitee", e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
                               <Label htmlFor="adresse_destinataire">Adresse destinataire *</Label>
              <Textarea
                id="adresse_destinataire"
                value={formData.adresse_destinataire}
                onChange={(e) => handleFormChange("adresse_destinataire", e.target.value)}
                placeholder="Adresse complète du destinataire"
                rows={3}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="adresse_enlevement">Adresse d'enlèvement *</Label>
              <Textarea
                id="adresse_enlevement"
                value={formData.adresse_enlevement}
                onChange={(e) => handleFormChange("adresse_enlevement", e.target.value)}
                placeholder="Adresse complète d'enlèvement"
                rows={3}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarques">Remarques</Label>
              <Textarea
                id="remarques"
                value={formData.remarques}
                onChange={(e) => handleFormChange("remarques", e.target.value)}
                placeholder="Remarques supplémentaires..."
                rows={2}
              />
            </div>
          </CardContent>
        </Card>

        {/* Gestion des produits */}
        <Card>
          <CardHeader>
            <CardTitle>Produits</CardTitle>
            <CardDescription>
              Ajoutez les produits à rapatrier
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Formulaire d'ajout de produit */}
            <div className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Ajouter un produit</h3>
                {produitFromStock && (
                  <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                    Pré-rempli depuis un stock externe
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="code_prdt">Code produit *</Label>
                  <Input
                    id="code_prdt"
                    value={currentProduit.code_prdt}
                    onChange={(e) => handleProduitChange("code_prdt", e.target.value)}
                    placeholder="Code produit"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="designation_prdt">Désignation *</Label>
                  <Input
                    id="designation_prdt"
                    value={currentProduit.designation_prdt}
                    onChange={(e) => handleProduitChange("designation_prdt", e.target.value)}
                    placeholder="Désignation du produit"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lot">Lot *</Label>
                  <Input
                    id="lot"
                    value={currentProduit.lot}
                    onChange={(e) => handleProduitChange("lot", e.target.value)}
                    placeholder="Numéro de lot"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="poids_net">Poids net (kg)</Label>
                  <Input
                    id="poids_net"
                    type="number"
                    step="0.01"
                    value={currentProduit.poids_net}
                    onChange={(e) => handleProduitChange("poids_net", parseFloat(e.target.value) || 0)}
                    placeholder="0.00"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="type_emballage">Type d'emballage</Label>
                  <Select
                    value={currentProduit.type_emballage}
                    onValueChange={(value) => handleProduitChange("type_emballage", value as TypeEmballage)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={TypeEmballage.CARTON}>Carton</SelectItem>
                      <SelectItem value={TypeEmballage.SAC}>Sac</SelectItem>
                      <SelectItem value={TypeEmballage.CONTENEUR}>Conteneur</SelectItem>
                      <SelectItem value={TypeEmballage.AUTRE}>Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nb_contenants">Nombre de contenants</Label>
                  <Input
                    id="nb_contenants"
                    type="number"
                    value={currentProduit.nb_contenants}
                    onChange={(e) => handleProduitChange("nb_contenants", parseInt(e.target.value) || 0)}
                    placeholder="0"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nb_palettes">Nombre de palettes</Label>
                  <Input
                    id="nb_palettes"
                    type="number"
                    value={currentProduit.nb_palettes}
                    onChange={(e) => handleProduitChange("nb_palettes", parseInt(e.target.value) || 0)}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dimension_palettes">Dimensions palettes</Label>
                  <Input
                    id="dimension_palettes"
                    value={currentProduit.dimension_palettes}
                    onChange={(e) => handleProduitChange("dimension_palettes", e.target.value)}
                    placeholder="ex: 120x80x150 cm"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="code_onu">Code ONU</Label>
                  <Input
                    id="code_onu"
                    value={currentProduit.code_onu}
                    onChange={(e) => handleProduitChange("code_onu", e.target.value)}
                    placeholder="Code ONU"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="grp_emballage">Groupe d'emballage</Label>
                  <Input
                    id="grp_emballage"
                    value={currentProduit.grp_emballage}
                    onChange={(e) => handleProduitChange("grp_emballage", e.target.value)}
                    placeholder="Groupe d'emballage"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="po">PO</Label>
                  <Input
                    id="po"
                    value={currentProduit.po}
                    onChange={(e) => handleProduitChange("po", e.target.value)}
                    placeholder="Numéro PO"
                  />
                </div>

                <div className="flex items-center space-x-2 pt-6">
                  <input
                    type="checkbox"
                    id="stock_solde"
                    checked={currentProduit.stock_solde}
                    onChange={(e) => handleProduitChange("stock_solde", e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="stock_solde">Stock soldé</Label>
                </div>
              </div>

              <Button
                type="button"
                onClick={handleAddProduit}
                className="w-full"
              >
                Ajouter le produit
              </Button>
            </div>

            {/* Liste des produits ajoutés */}
            {produits.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-semibold">Produits ajoutés ({produits.length})</h3>
                
                <div className="space-y-2">
                  {produits.map((produit, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg bg-muted/50"
                    >
                      <div className="flex-1">
                        <div className="font-medium">
                          {produit.code_prdt} - {produit.designation_prdt}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Lot: {produit.lot} | Poids: {produit.poids_net}kg | 
                          Contenants: {produit.nb_contenants} | Palettes: {produit.nb_palettes}
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveProduit(index)}
                      >
                        Supprimer
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Boutons d'action */}
        <div className="flex justify-end space-x-4">
          <Button
            variant="outline"
            onClick={() => router.push("/rappatriements")}
            disabled={isLoading}
          >
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading || produits.length === 0}
          >
            {isLoading ? "Création..." : "Créer le rapatriement"}
          </Button>
        </div>
      </div>
    </div>
  );
}
