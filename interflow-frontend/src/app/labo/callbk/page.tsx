'use client';

import { useState, useCallback, memo, useRef, useEffect } from 'react';

// Composant enfant mémorisé qui affiche combien de fois il a été rendu
const ChildButton = memo(({ onClick, label }: { onClick: () => void; label: string }) => {
  // Utiliser useRef pour compter les rendus sans causer de re-rendu
  const renderCount = useRef(0);
  
  // Incrémenter à chaque rendu
  renderCount.current += 1;

  // Logger dans useEffect pour éviter les problèmes d'hydration
  useEffect(() => {
    console.log(`${label} rendu ${renderCount.current} fois`);
  });

  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
    >
      {label} (Rendus: {renderCount.current})
    </button>
  );
});

ChildButton.displayName = 'ChildButton';

export default function UseCallbackDemo() {
  const [count, setCount] = useState(0);
  const [otherState, setOtherState] = useState(0);

  // ❌ SANS useCallback : cette fonction est recréée à chaque rendu
  // Cela provoque le re-rendu du ChildButton même si count ne change pas
  const handleIncrementWithoutCallback = () => {
    setCount(prev => prev + 1);
  };

  // ✅ AVEC useCallback : cette fonction est mémorisée
  // Elle n'est recréée QUE si 'count' change (dépendance)
  const handleIncrementWithCallback = useCallback(() => {
    setCount(prev => prev + 1);
  }, []); // Dépendances vides = fonction stable qui ne change jamais

  // Fonction avec dépendance
  const handleDoubleCount = useCallback(() => {
    setCount(count * 2);
  }, [count]); // Cette fonction sera recréée quand 'count' change

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Démonstration de useCallback</h1>
      
      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-4">État actuel</h2>
        <p className="text-2xl mb-2">Count: <span className="font-bold text-blue-600">{count}</span></p>
        <p className="text-2xl">Other State: <span className="font-bold text-green-600">{otherState}</span></p>
      </div>

      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-4">Commentaire</h2>
        <p className="text-sm text-gray-700">
            l'incrémentation est effectué 2 par 2 en dev mode, alors qu'en prod mode, elle est effectué 1 par 1 à cause du Strict mode actif en dev.
        </p>
      </div>

      <div className="space-y-8">
        {/* Section SANS useCallback */}
        <div className="border-2 border-red-300 p-6 rounded-lg bg-red-50">
          <h3 className="text-lg font-semibold mb-3 text-red-700">
            ❌ SANS useCallback
          </h3>
          <p className="mb-4 text-sm text-gray-700">
            Le bouton ci-dessous se re-rend à CHAQUE fois que le composant parent se re-rend,
            même si la fonction ne change pas logiquement.
          </p>
          <ChildButton 
            onClick={handleIncrementWithoutCallback} 
            label="Incrémenter (sans useCallback)"
          />
        </div>

        {/* Section AVEC useCallback */}
        <div className="border-2 border-green-300 p-6 rounded-lg bg-green-50">
          <h3 className="text-lg font-semibold mb-3 text-green-700">
            ✅ AVEC useCallback (count n'est pas dans les dépendances)
          </h3>
          <p className="mb-4 text-sm text-gray-700">
            Le bouton ci-dessous ne se re-rend QUE si ses props changent réellement.
            La fonction étant mémorisée, elle garde la même référence entre les rendus.
          </p>
          <ChildButton 
            onClick={handleIncrementWithCallback} 
            label="Incrémenter (avec useCallback)"
          />
        </div>

        {/* Section avec dépendances */}
        <div className="border-2 border-blue-300 p-6 rounded-lg bg-blue-50">
          <h3 className="text-lg font-semibold mb-3 text-blue-700">
            🔄 AVEC dépendances (count est dans les dépendances)
          </h3>
          <p className="mb-4 text-sm text-gray-700">
            Cette fonction utilise &apos;count&apos; dans son corps, donc &apos;count&apos; doit être dans les dépendances.
            Le bouton se re-rend quand &apos;count&apos; change.
          </p>
          <ChildButton 
            onClick={handleDoubleCount} 
            label="Doubler le count"
          />
        </div>

        {/* Bouton pour tester */}
        <div className="border-2 border-purple-300 p-6 rounded-lg bg-purple-50">
          <h3 className="text-lg font-semibold mb-3 text-purple-700">
            🧪 Test : Changer un autre état
          </h3>
          <p className="mb-4 text-sm text-gray-700">
            Cliquez ici pour changer &apos;otherState&apos;. Observez quels boutons se re-rendent !
          </p>
          <button
            onClick={() => setOtherState(prev => prev + 1)}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition"
          >
            Changer Other State
          </button>
        </div>
      </div>

      <div className="mt-8 p-6 bg-yellow-50 border border-yellow-300 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">📝 Points clés :</h3>
        <ul className="list-disc list-inside space-y-2 text-sm">
          <li><code className="bg-gray-200 px-1 rounded">useCallback</code> mémorise une fonction entre les rendus</li>
          <li>Utilisez-le avec <code className="bg-gray-200 px-1 rounded">React.memo()</code> pour optimiser les composants enfants</li>
          <li>La fonction est recréée seulement si une dépendance change</li>
          <li>Ouvrez la console pour voir les logs de re-rendu</li>
          <li>Sans useCallback, une nouvelle fonction est créée à chaque rendu, causant des re-rendus inutiles</li>
        </ul>
      </div>
    </div>
  );
}

