"use client";

import { useMutation } from "@tanstack/react-query";
import { downloadFDS } from "@/services/matiere-service";

// Hook pour télécharger une FDS
export function useDownloadFDS() {
  return useMutation({
    mutationFn: (code_mp: string) => downloadFDS(code_mp),
    onSuccess: (url) => {
      // Ouvrir le lien de téléchargement dans un nouvel onglet
      window.open(url, '_blank');
    },
  });
} 