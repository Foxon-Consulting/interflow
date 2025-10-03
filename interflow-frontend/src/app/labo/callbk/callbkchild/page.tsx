'use client';

import { useState, memo, useRef, useEffect } from 'react';

// 🔴 Composant SANS React.memo
// Se re-rend à CHAQUE fois que le parent se re-rend, même si les props n'ont pas changé
function ComposantNormal({ value, label }: { value: number; label: string }) {
  const renderCount = useRef(0);
  renderCount.current += 1;

  useEffect(() => {
    console.log(`[NORMAL] ${label} rendu ${renderCount.current} fois`);
  });

  return (
    <div className="p-4 bg-red-100 border-2 border-red-400 rounded">
      <h4 className="font-semibold text-red-700 mb-2">Sans React.memo</h4>
      <p className="text-sm mb-1">Value: {value}</p>
      <p className="text-sm">Rendus: {renderCount.current}</p>
    </div>
  );
}

// 🟢 Composant AVEC React.memo
// Ne se re-rend QUE si les props changent réellement
const ComposantMemorise = memo(({ value, label }: { value: number; label: string }) => {
  const renderCount = useRef(0);
  renderCount.current += 1;

  useEffect(() => {
    console.log(`[MEMO] ${label} rendu ${renderCount.current} fois`);
  });

  return (
    <div className="p-4 bg-green-100 border-2 border-green-400 rounded">
      <h4 className="font-semibold text-green-700 mb-2">Avec React.memo</h4>
      <p className="text-sm mb-1">Value: {value}</p>
      <p className="text-sm">Rendus: {renderCount.current}</p>
    </div>
  );
});

ComposantMemorise.displayName = 'ComposantMemorise';

// 🔵 Composant AVEC React.memo et comparaison personnalisée
const ComposantMemoAvance = memo(
  ({ value, label }: { value: number; label: string }) => {
    const renderCount = useRef(0);
    renderCount.current += 1;

    useEffect(() => {
      console.log(`[MEMO AVANCÉ] ${label} rendu ${renderCount.current} fois`);
    });

    return (
      <div className="p-4 bg-blue-100 border-2 border-blue-400 rounded">
        <h4 className="font-semibold text-blue-700 mb-2">
          Avec React.memo + comparaison custom
        </h4>
        <p className="text-sm mb-1">Value (pairs seulement): {value}</p>
        <p className="text-sm">Rendus: {renderCount.current}</p>
      </div>
    );
  },
  // Fonction de comparaison personnalisée
  // Retourne true si les props sont "égales" (ne pas re-rendre)
  // Retourne false si les props ont changé (re-rendre)
  (prevProps, nextProps) => {
    // Ne re-rendre que si on passe d'un nombre pair à un autre nombre pair
    // Ignorer les nombres impairs
    const prevEven = prevProps.value % 2 === 0;
    const nextEven = nextProps.value % 2 === 0;
    
    // Si les deux sont pairs ou impairs, comparer normalement
    if (prevEven && nextEven) {
      return prevProps.value === nextProps.value;
    }
    
    // Si on passe de pair à impair ou vice-versa, ne pas re-rendre
    return true;
  }
);

ComposantMemoAvance.displayName = 'ComposantMemoAvance';

export default function ReactMemoDemo() {
  const [compteur, setCompteur] = useState(0);
  const [autreEtat, setAutreEtat] = useState(0);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Démonstration de React.memo</h1>

      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-4">État du parent</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-lg mb-2">
              Compteur: <span className="font-bold text-blue-600">{compteur}</span>
            </p>
            <button
              onClick={() => setCompteur(prev => prev + 1)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Incrémenter Compteur
            </button>
          </div>
          
          <div>
            <p className="text-lg mb-2">
              Autre État: <span className="font-bold text-purple-600">{autreEtat}</span>
            </p>
            <button
              onClick={() => setAutreEtat(prev => prev + 1)}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              Incrémenter Autre État
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Composant normal */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="text-2xl mr-2">🔴</span>
            Composant SANS React.memo
          </h3>
          <p className="text-sm text-gray-600 mb-3">
            Ce composant se re-rend à CHAQUE fois que le parent se re-rend,
            même si ses props (value={compteur}) ne changent pas.
          </p>
          <ComposantNormal value={compteur} label="Normal" />
          <p className="text-xs text-gray-500 mt-2">
            ⚠️ Cliquez sur &quot;Incrémenter Autre État&quot; et voyez le compteur de rendus augmenter !
          </p>
        </div>

        {/* Composant mémorisé */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="text-2xl mr-2">🟢</span>
            Composant AVEC React.memo
          </h3>
          <p className="text-sm text-gray-600 mb-3">
            Ce composant ne se re-rend QUE si ses props (value={compteur}) changent.
            Il ignore les changements de &apos;autreEtat&apos;.
          </p>
          <ComposantMemorise value={compteur} label="Mémorisé" />
          <p className="text-xs text-gray-500 mt-2">
            ✅ Cliquez sur &quot;Incrémenter Autre État&quot; → pas de re-rendu !
          </p>
        </div>

        {/* Composant avec comparaison personnalisée */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="text-2xl mr-2">🔵</span>
            Composant AVEC React.memo + comparaison personnalisée
          </h3>
          <p className="text-sm text-gray-600 mb-3">
            Ce composant utilise une fonction de comparaison personnalisée :
            il ne se re-rend que quand la valeur du compteur change ET est paire.
            Les nombres impairs sont ignorés !
          </p>
          <ComposantMemoAvance value={compteur} label="Mémorisé Avancé" />
          <p className="text-xs text-gray-500 mt-2">
            🎯 Regardez : seuls les nombres pairs déclenchent un re-rendu !
          </p>
        </div>
      </div>

      {/* Section d'explication */}
      <div className="mt-8 p-6 bg-yellow-50 border border-yellow-300 rounded-lg">
        <h3 className="text-lg font-semibold mb-3">📚 Comprendre React.memo</h3>
        
        <div className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold mb-1">🤔 Qu&apos;est-ce que React.memo ?</h4>
            <p>
              <code className="bg-gray-200 px-1 rounded">React.memo</code> est un HOC 
              (Higher Order Component) qui mémorise un composant. Il compare les props 
              et ne re-rend le composant que si elles ont changé.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-1">📊 Comparaison par défaut</h4>
            <p>
              Par défaut, React.memo fait une comparaison <strong>superficielle</strong> (shallow) 
              des props. Si les props sont des primitives (number, string, boolean), 
              ça fonctionne parfaitement.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-1">🎨 Comparaison personnalisée</h4>
            <p>
              Vous pouvez fournir une fonction de comparaison personnalisée comme 
              deuxième argument :
            </p>
            <pre className="bg-gray-100 p-2 rounded mt-2 text-xs overflow-x-auto">
{`const MonComposant = memo(
  ({ value }) => <div>{value}</div>,
  (prevProps, nextProps) => {
    // Retourne true pour NE PAS re-rendre
    // Retourne false pour re-rendre
    return prevProps.value === nextProps.value;
  }
);`}
            </pre>
          </div>

          <div>
            <h4 className="font-semibold mb-1">⚡ Quand utiliser React.memo ?</h4>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Composants qui se re-rendent souvent avec les mêmes props</li>
              <li>Composants avec un rendu coûteux (calculs lourds, grandes listes)</li>
              <li>En combinaison avec <code className="bg-gray-200 px-1 rounded">useCallback</code> 
              et <code className="bg-gray-200 px-1 rounded">useMemo</code></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-1">⚠️ Quand NE PAS utiliser React.memo ?</h4>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Composants qui se re-rendent rarement</li>
              <li>Composants avec des props qui changent souvent</li>
              <li>Optimisation prématurée (mesurez d&apos;abord !)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-300 rounded">
        <p className="text-sm">
          💡 <strong>Astuce :</strong> Ouvrez la console pour voir les logs détaillés 
          des rendus de chaque composant !
        </p>
      </div>
    </div>
  );
}

