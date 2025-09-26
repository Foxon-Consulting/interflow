"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path;
  };

  return (
    <nav className="flex items-center space-x-4 lg:space-x-6 mb-8">
      {/* <Link 
        href="/" 
        className={`text-sm font-medium transition-colors hover:text-primary ${
          isActive("/") 
            ? "text-primary" 
            : "text-muted-foreground"
        }`}
      >
        Accueil
      </Link> */}
      <Link 
        href="/besoins" 
        className={`text-sm font-medium transition-colors hover:text-primary ${
          isActive("/besoins") 
            ? "text-primary" 
            : "text-muted-foreground"
        }`}
      >
        Besoins
      </Link>
      <Link 
        href="/stocks" 
        className={`text-sm font-medium transition-colors hover:text-primary ${
          isActive("/stocks") 
            ? "text-primary" 
            : "text-muted-foreground"
        }`}
      >
        Stocks
      </Link>
        <Link 
          href="/receptions" 
          className={`text-sm font-medium transition-colors hover:text-primary ${
            isActive("/receptions") 
              ? "text-primary" 
              : "text-muted-foreground"
          }`}
        >
          Réceptions
        </Link>
        
        
      <Link 
          href="/rappatriements" 
          className={`text-sm font-medium transition-colors hover:text-primary ${
            isActive("/rappatriements") 
              ? "text-primary" 
              : "text-muted-foreground"
          }`}
        >
          Rapatriements
        </Link>
        <Link 
          href="/analyses" 
          className={`text-sm font-medium transition-colors hover:text-primary ${
            isActive("/analyses") 
              ? "text-primary" 
              : "text-muted-foreground"
          }`}
        >
          Analyses
        </Link>
        <Link 
          href="/matieres" 
          className={`text-sm font-medium transition-colors hover:text-primary ${
            isActive("/matieres") 
              ? "text-primary" 
              : "text-muted-foreground"
          }`}
      >
        Références Matières
      </Link>
    </nav>
  );
}

export function NavigationClient() {
  return <Navigation />;
} 