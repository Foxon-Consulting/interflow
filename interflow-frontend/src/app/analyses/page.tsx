"use client"

import { ChartBarStacked } from "@/components/ui/barchart"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { useState, useEffect, useCallback, useMemo } from "react"
import { AnalyseService } from "@/services/analyse-service"

// Interfaces pour les données d'analyse
interface AnalyseData {
  comparaison: string;
  besoin: number;
  stocks_internes: number;
  receptions: number;
  rappatriements: number;
  [key: string]: number | string;
}

// Interface pour le besoin chargé
interface BesoinCharge {
  id: number;
  code_mp: string;
  nom_matiere: string;
  quantite: number;
  echeance: string;
  etat: string;
  lot: string | null;
}
import { CheckCircle, XCircle, AlertTriangle } from "lucide-react"
  
export default function AnalysesPage() {
  // Données par défaut
  const defaultData: AnalyseData[] = useMemo(() => [
      { comparaison: "besoin", besoin: 0, stocks_internes: 0, receptions: 0, rappatriements: 0 },
  { comparaison: "stock", besoin: 0, stocks_internes: 0, receptions: 0, rappatriements: 0, EXMC: 0, EXMP: 0 },
  ] as AnalyseData[], [])

  // Configuration de base
  const baseConfig: { [key: string]: { label: string; color: string } } = useMemo(() => ({
    besoin: {
      label: "Besoin",
      color: "var(--chart-1)",
    },
    stocks_internes: {
      label: "Stocks Internes",
      color: "var(--chart-2)",
    },
      receptions: {
    label: "Réceptions",
    color: "var(--chart-3)",
  },
    rappatriements: {
      label: "Rappatriements",
      color: "var(--chart-4)",
    },
  }), [])

  // Configuration dynamique pour les magasins externes
  const [dynamicConfig, setDynamicConfig] = useState(baseConfig)
  const [showStocksExternes, setShowStocksExternes] = useState(false)
  const [analyseResult, setAnalyseResult] = useState<any>(null)
  const [horizonDays, setHorizonDays] = useState(5)
  const [dateInitiale, setDateInitiale] = useState(new Date().toISOString().split('T')[0])

  // Récupérer le code MP sauvegardé depuis localStorage
  const getSavedCodeMp = (): string => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('analyses_code_mp') || ""
    }
    return ""
  }

  // Sauvegarder le code MP dans localStorage
  const saveCodeMp = (codeMp: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('analyses_code_mp', codeMp)
    }
  }

  const [codeMp, setCodeMp] = useState(getSavedCodeMp)
  const [customData, setCustomData] = useState<AnalyseData[]>(defaultData)
  const [isLoading, setIsLoading] = useState(false)
  const [besoinCharge, setBesoinCharge] = useState<BesoinCharge | null>(null)

  // Récupérer les données du besoin depuis localStorage
  const getBesoinData = (): BesoinCharge | null => {
    if (typeof window !== 'undefined') {
      const besoinData = localStorage.getItem('analyses_besoin_data')
      return besoinData ? JSON.parse(besoinData) : null
    }
    return null
  }

  // Fonction pour charger les données
  const chargerDonnees = useCallback(async (codeMpToLoad: string) => {
    if (!codeMpToLoad.trim()) {
      // Si aucun code MP n'est saisi, utiliser les données par défaut
      setCustomData(defaultData)
      setAnalyseResult(null)
      return
    }

    setIsLoading(true)
    try {
      // console.log(`📊 [ANALYSES-PAGE] Chargement des données pour le code MP: ${codeMpToLoad}`)
      
      // Récupérer les données complètes d'analyse
      const result = await AnalyseService.calculerQuantites(codeMpToLoad.trim(), horizonDays, dateInitiale)
      setAnalyseResult(result)
      
      // Générer les données pour le graphique
      const donnees = await AnalyseService.genererDonneesGraphique(codeMpToLoad.trim(), horizonDays, dateInitiale)
      setCustomData(donnees)
      
      // Mettre à jour la configuration dynamique avec les magasins trouvés
      const stockData = donnees.find(d => d.comparaison === "stock")
      if (stockData) {
        const magasinsExternes = Object.keys(stockData).filter(key => 
          key !== 'comparaison' && 
          key !== 'besoin' && 
          key !== 'stocks_internes' && 
          key !== 'receptions' && 
          key !== 'rappatriements'
        )
        
        const newConfig = { ...baseConfig }
        magasinsExternes.forEach((magasin, index) => {
          newConfig[magasin] = {
            label: `Stocks ${magasin}`,
            color: `var(--chart-${5 + index})`,
          }
        })
        setDynamicConfig(newConfig)
      }
      
      // console.log(`✅ [ANALYSES-PAGE] Données chargées:`, donnees)
    } catch (error) {
      console.error(`❌ [ANALYSES-PAGE] Erreur lors du chargement des données:`, error)
      // En cas d'erreur, utiliser les données par défaut
      setCustomData(defaultData)
      setAnalyseResult(null)
    } finally {
      setIsLoading(false)
    }
  }, [horizonDays, dateInitiale, baseConfig, defaultData])

  // Effet pour charger les données au montage du composant si un code MP est sauvegardé
  useEffect(() => {
    const savedCodeMp = getSavedCodeMp()
    const besoinData = getBesoinData()
    
    if (besoinData) {
      setBesoinCharge(besoinData)
      // Nettoyer le localStorage après récupération
      localStorage.removeItem('analyses_besoin_data')
    }
    
    if (savedCodeMp.trim()) {
      // console.log(`📊 [ANALYSES-PAGE] Code MP sauvegardé trouvé: ${savedCodeMp}, chargement automatique des données`)
      chargerDonnees(savedCodeMp)
    }
  }, [chargerDonnees])

  // Effet pour charger les données quand le code MP change
  useEffect(() => {
    // Sauvegarder le code MP dans localStorage
    saveCodeMp(codeMp)

    // Délai pour éviter trop d'appels API pendant la saisie
    const timeoutId = setTimeout(() => {
      chargerDonnees(codeMp)
    }, 500)
    
    return () => clearTimeout(timeoutId)
  }, [codeMp, chargerDonnees])

  // Déterminer les clés à afficher selon l'état du toggle
  const getBarKeys = () => {
    const baseKeys = ["besoin", "stocks_internes", "receptions", "rappatriements"]
    if (!showStocksExternes) return baseKeys
    
    // Ajouter les magasins externes trouvés dans les données
    const stockData = customData.find(d => d.comparaison === "stock")
    if (stockData) {
      const magasinsExternes = Object.keys(stockData).filter(key => 
        key !== 'comparaison' && 
        key !== 'besoin' && 
        key !== 'stocks_internes' && 
        key !== 'receptions' && 
        key !== 'rappatriements'
      )
      return [...baseKeys, ...magasinsExternes]
    }
    
    return baseKeys
  }



  // Fonction pour déterminer le statut de couverture
  const getStatutCouverture = () => {
    if (!customData || customData.length === 0) return { 
      statut: "Couvert", 
      couleur: "text-green-600",
      icon: CheckCircle,
      color: "#16a34a"
    }
    
    const besoinData = customData.find(d => d.comparaison === "besoin")
    const stockData = customData.find(d => d.comparaison === "stock")
    
    if (!besoinData || !stockData) return { 
      statut: "Couvert", 
      couleur: "text-green-600",
      icon: CheckCircle,
      color: "#16a34a"
    }
    
    const besoins = Number(besoinData.besoin) || 0
    const stockInterne = Number(stockData.stocks_internes) || 0
    const rappatriements = Number(stockData.rappatriements) || 0
    const receptions = Number(stockData.receptions) || 0
    
    // Calculer le stock total disponible (interne + rappatriements + réceptions)
    const stockTotal = stockInterne + rappatriements + receptions
    
    // Ajouter les stocks externes si disponibles
    const stocksExternes = Object.keys(stockData).filter(key => 
      key !== 'comparaison' && 
      key !== 'besoin' && 
      key !== 'stocks_internes' && 
              key !== 'receptions' &&  
      key !== 'rappatriements'
    ).reduce((total, key) => total + (stockData[key as keyof typeof stockData] as number || 0), 0)
    
    const stockTotalAvecExternes = stockTotal + stocksExternes
    
    if (besoins > stockTotalAvecExternes) {
      return { 
        statut: "Pénurie", 
        couleur: "text-red-600",
        icon: XCircle,
        color: "#dc2626"
      }
    } else if (besoins > stockTotal) {
      return { 
        statut: "Déficit", 
        couleur: "text-orange-600",
        icon: AlertTriangle,
        color: "#ea580c"
      }
    } else {
      return { 
        statut: "Couvert", 
        couleur: "text-green-600",
        icon: CheckCircle,
        color: "#16a34a"
      }
    }
  }

  return (
    <div>
      <div className="text-2xl font-bold">Analyses</div>

      {/* Affichage du besoin chargé */}
      {besoinCharge && (
        <Card className="mt-4 mb-6">
          <CardHeader>
            <CardTitle className="text-lg text-blue-600">Besoin chargé depuis la liste</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-600">Code MP</Label>
                <p className="text-lg font-semibold">{besoinCharge.code_mp}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Matière</Label>
                <p className="text-lg font-semibold">{besoinCharge.nom_matiere}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Quantité</Label>
                <p className="text-lg font-semibold">{besoinCharge.quantite}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Échéance</Label>
                <p className="text-lg font-semibold">{new Date(besoinCharge.echeance).toLocaleDateString('fr-FR')}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">État</Label>
                <p className="text-lg font-semibold">{besoinCharge.etat}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Lot</Label>
                <p className="text-lg font-semibold">{besoinCharge.lot || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Contrôles pour l'analyse */}
      <div className="mt-4 space-y-4">
        {/* Ligne 1: Code MP et bouton stocks externes */}
        <div className="flex justify-center gap-2 items-center">
          <Input 
            type="text" 
            placeholder="Code mp" 
            value={codeMp} 
            onChange={(e) => setCodeMp(e.target.value)}
            className="max-w-xs"
          />
          <Button
            variant={showStocksExternes ? "default" : "outline"}
            onClick={() => setShowStocksExternes(!showStocksExternes)}
            className="whitespace-nowrap"
          >
            {showStocksExternes ? "Masquer" : "Afficher"} Stocks Externes
          </Button>
        </div>

        {/* Ligne 2: Horizon et date initiale */}
        <div className="flex justify-center gap-4 items-center">
          <div className="flex items-center gap-2">
            <Label htmlFor="horizon" className="text-sm font-medium">Horizon (jours):</Label>
            <Input
              id="horizon"
              type="number"
              min="1"
              max="30"
              value={horizonDays}
              onChange={(e) => setHorizonDays(parseInt(e.target.value) || 5)}
              className="w-20"
            />
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="date" className="text-sm font-medium">Date initiale:</Label>
            <Input
              id="date"
              type="date"
              value={dateInitiale}
              onChange={(e) => setDateInitiale(e.target.value)}
              className="w-40"
            />
          </div>
        </div>
      </div>
      
      {/* Indicateur de chargement */}
      {isLoading && (
        <div className="flex justify-center mt-2">
          <div className="text-sm text-gray-600">Chargement des données...</div>
        </div>
      )}

      {/* Utilisation avec données personnalisées */}
      <div className="mt-6">
        <ChartBarStacked 
          data={customData}
          title="Analyses de couverture"
          description={codeMp ? `Code mp: ${codeMp} - Horizon: ${horizonDays} jours - Date: ${dateInitiale}` : "Code mp"}
          config={dynamicConfig}
          xAxisKey="comparaison"
          barKeys={getBarKeys()}
          trendText={getStatutCouverture().statut}
          trendColor={getStatutCouverture().color}
          trendIcon={getStatutCouverture().icon}
          footerText="Affichage des stocks"
        />
      </div>

      
      {/* Informations détaillées de l'analyse */}
      {analyseResult && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <Card className="p-3">
            <CardHeader className="pb-1 px-0 pt-0">
              <CardTitle className="text-xs font-medium">Matière</CardTitle>
            </CardHeader>
            <CardContent className="px-0 pb-0">
              <div className="text-sm font-semibold">{analyseResult?.nom_matiere || codeMp}</div>
              <div className="text-xs text-gray-600">Code: {codeMp}</div>
            </CardContent>
          </Card>

          <Card className="p-3">
            <CardHeader className="pb-1 px-0 pt-0">
              <CardTitle className="text-xs font-medium">Stock Total Disponible</CardTitle>
            </CardHeader>
            <CardContent className="px-0 pb-0">
              <div className="text-sm font-semibold">
                {analyseResult?.quantite_totale_disponible?.toLocaleString() || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="p-3">
            <CardHeader className="pb-1 px-0 pt-0">
              <CardTitle className="text-xs font-medium">Stock Manquant</CardTitle>
            </CardHeader>
            <CardContent className="px-0 pb-0">
              <div className={`text-sm font-semibold ${(analyseResult?.stock_manquant || 0) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {analyseResult?.stock_manquant?.toLocaleString() || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
    </div>
  )
}