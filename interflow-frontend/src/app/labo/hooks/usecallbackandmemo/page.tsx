'use client';

import { useState, useCallback, memo, useRef, useEffect } from 'react';

// 🔴 Cas 1 : React.memo SEUL (SANS useCallback dans le parent)
// Problème : React.memo ne sert à rien car la fonction change à chaque rendu
const BoutonAvecMemoSeul = memo(({ onClick, label }: { onClick: () => void; label: string }) => {
  const renderCount = useRef(0);
  renderCount.current += 1;

  useEffect(() => {
    console.log(`[MEMO SEUL] ${label} - Rendu #${renderCount.current}`);
  });

  return (
    <button 
      onClick={onClick}
      className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
    >
      {label} (Rendus: {renderCount.current})
    </button>
  );
});

BoutonAvecMemoSeul.displayName = 'BoutonAvecMemoSeul';

// 🟡 Cas 2 : useCallback SEUL (composant enfant SANS memo)
// Problème : useCallback ne sert à rien car le composant se re-rend quand même
function BoutonAvecCallbackSeul({ onClick, label }: { onClick: () => void; label: string }) {
  const renderCount = useRef(0);
  renderCount.current += 1;

  useEffect(() => {
    console.log(`[CALLBACK SEUL] ${label} - Rendu #${renderCount.current}`);
  });

  return (
    <button 
      onClick={onClick}
      className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
    >
      {label} (Rendus: {renderCount.current})
    </button>
  );
}

// 🟢 Cas 3 : React.memo + useCallback ENSEMBLE
// ✅ Solution optimale : les deux travaillent ensemble !
const BoutonOptimise = memo(({ onClick, label }: { onClick: () => void; label: string }) => {
  const renderCount = useRef(0);
  renderCount.current += 1;

  useEffect(() => {
    console.log(`[OPTIMISÉ] ${label} - Rendu #${renderCount.current}`);
  });

  return (
    <button 
      onClick={onClick}
      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
    >
      {label} (Rendus: {renderCount.current})
    </button>
  );
});

BoutonOptimise.displayName = 'BoutonOptimise';

export default function UseCallbackEtMemoDemo() {
  const [count, setCount] = useState(0);
  const [otherState, setOtherState] = useState(0);

  // ❌ Fonction normale : recréée à chaque rendu
  const handleClickNormal = () => {
    setCount(prev => prev + 1);
  };

  // ✅ Fonction mémorisée avec useCallback
  const handleClickMemorise = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">
        React.memo + useCallback : Pourquoi les deux ?
      </h1>

      {/* État du parent */}
      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-4">Contrôles</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-lg mb-2">
              Count: <span className="font-bold text-blue-600">{count}</span>
            </p>
          </div>
          <div>
            <p className="text-lg mb-2">
              Other State: <span className="font-bold text-purple-600">{otherState}</span>
            </p>
            <button
              onClick={() => setOtherState(prev => prev + 1)}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              Changer Other State
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        {/* Cas 1 : React.memo SEUL */}
        <div className="border-2 border-red-400 p-6 rounded-lg bg-red-50">
          <h3 className="text-xl font-semibold mb-3 text-red-700">
            🔴 Cas 1 : React.memo SEUL (SANS useCallback)
          </h3>
          
          <div className="mb-4 p-4 bg-white rounded">
            <h4 className="font-semibold mb-2">Code :</h4>
            <pre className="text-xs bg-gray-800 text-white p-3 rounded overflow-x-auto">
{`// Parent
const handleClick = () => { ... };  // ❌ Recréée à chaque rendu

// Enfant
const Bouton = memo(({ onClick }) => {
  return <button onClick={onClick}>Click</button>;
});

<Bouton onClick={handleClick} />  // ❌ onClick change → re-rendu`}
            </pre>
          </div>

          <div className="mb-4">
            <p className="text-sm mb-2">
              <strong>Problème :</strong> Même si le composant enfant utilise <code className="bg-gray-200 px-1">memo</code>,
              la fonction <code className="bg-gray-200 px-1">handleClickNormal</code> est recréée à chaque rendu du parent.
              React.memo détecte que la prop <code className="bg-gray-200 px-1">onClick</code> a changé (nouvelle référence)
              et re-rend le composant.
            </p>
            <p className="text-sm font-semibold text-red-700">
              ➡️ React.memo est INUTILE sans useCallback pour les props de type fonction !
            </p>
          </div>

          <BoutonAvecMemoSeul onClick={handleClickNormal} label="Cliquez-moi" />
          
          <p className="text-xs text-gray-600 mt-2">
            Cliquez sur &quot;Changer Other State&quot; et observez que ce bouton se re-rend quand même !
          </p>
        </div>

        {/* Cas 2 : useCallback SEUL */}
        <div className="border-2 border-yellow-400 p-6 rounded-lg bg-yellow-50">
          <h3 className="text-xl font-semibold mb-3 text-yellow-700">
            🟡 Cas 2 : useCallback SEUL (SANS React.memo)
          </h3>
          
          <div className="mb-4 p-4 bg-white rounded">
            <h4 className="font-semibold mb-2">Code :</h4>
            <pre className="text-xs bg-gray-800 text-white p-3 rounded overflow-x-auto">
{`// Parent
const handleClick = useCallback(() => { ... }, []);  // ✅ Mémorisée

// Enfant
function Bouton({ onClick }) {  // ❌ Pas de memo
  return <button onClick={onClick}>Click</button>;
}

<Bouton onClick={handleClick} />  // ❌ Se re-rend quand même`}
            </pre>
          </div>

          <div className="mb-4">
            <p className="text-sm mb-2">
              <strong>Problème :</strong> La fonction <code className="bg-gray-200 px-1">handleClickMemorise</code> 
              est bien mémorisée avec useCallback, MAIS le composant enfant n&apos;utilise pas <code className="bg-gray-200 px-1">memo</code>.
              Donc quand le parent se re-rend, l&apos;enfant se re-rend aussi par défaut (comportement React normal).
            </p>
            <p className="text-sm font-semibold text-yellow-700">
              ➡️ useCallback est INUTILE sans React.memo sur le composant enfant !
            </p>
          </div>

          <BoutonAvecCallbackSeul onClick={handleClickMemorise} label="Cliquez-moi" />
          
          <p className="text-xs text-gray-600 mt-2">
            Cliquez sur &quot;Changer Other State&quot; et observez que ce bouton se re-rend aussi !
          </p>
        </div>

        {/* Cas 3 : React.memo + useCallback */}
        <div className="border-2 border-green-400 p-6 rounded-lg bg-green-50">
          <h3 className="text-xl font-semibold mb-3 text-green-700">
            🟢 Cas 3 : React.memo + useCallback ENSEMBLE
          </h3>
          
          <div className="mb-4 p-4 bg-white rounded">
            <h4 className="font-semibold mb-2">Code :</h4>
            <pre className="text-xs bg-gray-800 text-white p-3 rounded overflow-x-auto">
{`// Parent
const handleClick = useCallback(() => { ... }, []);  // ✅ Mémorisée

// Enfant
const Bouton = memo(({ onClick }) => {  // ✅ Mémorisé
  return <button onClick={onClick}>Click</button>;
});

<Bouton onClick={handleClick} />  // ✅ Pas de re-rendu inutile !`}
            </pre>
          </div>

          <div className="mb-4">
            <p className="text-sm mb-2">
              <strong>Solution :</strong> En combinant les deux :
            </p>
            <ul className="text-sm list-disc list-inside space-y-1 ml-2">
              <li><code className="bg-gray-200 px-1">useCallback</code> garde la même référence de fonction</li>
              <li><code className="bg-gray-200 px-1">memo</code> compare les props et évite le re-rendu</li>
              <li>Les deux travaillent ensemble pour optimiser les performances</li>
            </ul>
            <p className="text-sm font-semibold text-green-700 mt-2">
              ✅ C&apos;est la combinaison gagnante : pas de re-rendu inutile !
            </p>
          </div>

          <BoutonOptimise onClick={handleClickMemorise} label="Cliquez-moi" />
          
          <p className="text-xs text-gray-600 mt-2">
            Cliquez sur &quot;Changer Other State&quot; → ce bouton ne se re-rend PAS ! 🎉
          </p>
        </div>
      </div>

      {/* Section explicative */}
      <div className="mt-8 p-6 bg-blue-50 border border-blue-300 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">🎓 Comprendre la relation</h3>
        
        <div className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold mb-2">🤔 Pourquoi les deux sont nécessaires ?</h4>
            <p className="mb-2">
              En JavaScript, une fonction est un <strong>objet</strong>. À chaque rendu du parent,
              une nouvelle fonction est créée avec une nouvelle référence en mémoire :
            </p>
            <pre className="bg-gray-800 text-white p-3 rounded text-xs">
{`// Rendu 1
const fn1 = () => { ... };  // Référence A

// Rendu 2 (même code !)
const fn2 = () => { ... };  // Référence B (différente !)

fn1 === fn2  // false ! Ce sont deux objets différents`}
            </pre>
          </div>

          <div>
            <h4 className="font-semibold mb-2">🔗 La chaîne de dépendances</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-red-100 p-3 rounded">
                <p className="font-semibold text-red-700 mb-1">Sans optimisation</p>
                <p className="text-xs">
                  ❌ Fonction recréée<br/>
                  ❌ Props changent<br/>
                  ❌ Re-rendu systématique
                </p>
              </div>
              
              <div className="bg-yellow-100 p-3 rounded">
                <p className="font-semibold text-yellow-700 mb-1">Optimisation partielle</p>
                <p className="text-xs">
                  ⚠️ Un seul des deux<br/>
                  ⚠️ Ne suffit pas<br/>
                  ⚠️ Re-rendu quand même
                </p>
              </div>
              
              <div className="bg-green-100 p-3 rounded">
                <p className="font-semibold text-green-700 mb-1">Optimisation complète</p>
                <p className="text-xs">
                  ✅ useCallback + memo<br/>
                  ✅ Props stables<br/>
                  ✅ Pas de re-rendu inutile
                </p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">📋 Règle simple</h4>
            <div className="bg-white p-4 rounded border-l-4 border-blue-500">
              <p className="mb-2">
                Si vous passez une <strong>fonction</strong> en prop à un composant mémorisé :
              </p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Enveloppez la fonction dans <code className="bg-gray-200 px-1">useCallback</code> (parent)</li>
                <li>Enveloppez le composant dans <code className="bg-gray-200 px-1">memo</code> (enfant)</li>
                <li>Les deux ensemble = performances optimales !</li>
              </ol>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">💰 Autres props (pas de fonctions)</h4>
            <p>
              Pour les props <strong>primitives</strong> (number, string, boolean) ou les objets avec <code className="bg-gray-200 px-1">useMemo</code>,
              React.memo seul suffit car la comparaison par valeur fonctionne :
            </p>
            <pre className="bg-gray-800 text-white p-3 rounded text-xs mt-2">
{`const Bouton = memo(({ count, label }) => {
  // count et label sont des primitives
  // memo seul suffit (pas besoin de useCallback)
  return <button>{label}: {count}</button>;
});

<Bouton count={5} label="Click" />  // ✅ Optimisé`}
            </pre>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-purple-50 border border-purple-300 rounded">
        <p className="text-sm">
          💡 <strong>Test :</strong> Cliquez plusieurs fois sur &quot;Changer Other State&quot; 
          et observez les compteurs de rendus. Ouvrez la console pour voir les logs détaillés !
        </p>
      </div>
    </div>
  );
}

