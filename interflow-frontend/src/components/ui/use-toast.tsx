"use client"

type ToastProps = {
  title: string
  description?: string
  variant?: "default" | "success" | "destructive"
}

// Version simplifiée de toast pour cette démonstration
export function toast(_props: ToastProps) {
  // Dans une application réelle, cette fonction utiliserait une bibliothèque de toast
  // ou afficherait un vrai toast dans l'interface utilisateur
  // console.log(`Toast: ${_props.title} - ${_props.description || ""}`)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
} 