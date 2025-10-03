import { Navigation } from "@/components/navigation";

interface PageContainerProps {
  children: React.ReactNode;
}

export function PageContainer({ children }: PageContainerProps) {
  return (
    <div className="container mx-auto px-4 py-6">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">INTERFLOW</h1>
          <p className="text-sm text-muted-foreground">
            Visualisez et analysez vos données
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="rounded-full w-8 h-8 bg-primary text-primary-foreground flex items-center justify-center">
            <span className="sr-only">Notifications</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
              <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
            </svg>
          </button>
          <div className="rounded-full w-8 h-8 bg-gray-200 flex items-center justify-center">
            <span className="sr-only">Profil</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
      </header>
      
      <Navigation />
      
      <main>
        {children}
      </main>
      
      <footer className="mt-12 py-6 border-t text-center text-sm text-muted-foreground">
        <p>© MANE (EN) - Copyright 2025</p>
      </footer>
    </div>
  );
} 