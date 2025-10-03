"use client";
import { useState, useEffect } from "react";

export default function Horloge() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);

    // cleanup : éviter une fuite mémoire
    return () => clearInterval(timer);
  }, []); // [] = exécute l'effet une seule fois au montage

  return <p>Heure actuelle : {time.toLocaleTimeString()}</p>;
}
