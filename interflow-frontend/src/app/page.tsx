import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl mb-2">
          SmartLogistics
        </h1>
        <p className="text-muted-foreground">
          Gestion de commandes
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Carte Besoins */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Besoins opérationnels</CardTitle>
            <CardDescription>
              Gérer vos besoins opérationnels
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-24 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                <path d="M7 7h10"></path>
                <path d="M7 11h10"></path>
                <path d="M7 15h10"></path>
              </svg>
            </div>
            <div className="mt-4">
              <a href="/besoins" className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full">
                Accéder au Besoins
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Carte Stock */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Stock</CardTitle>
            <CardDescription>
              Consultez et gérez vos inventaires
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-24 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M20 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2Z"></path>
                <path d="M8 10v4"></path>
                <path d="M12 8v8"></path>
                <path d="M16 6v10"></path>
              </svg>
            </div>
            <div className="mt-4">
              <a href="/stock" className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full">
                Gérer le stock
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Carte Réceptions */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Réceptions</CardTitle>
            <CardDescription>
              Suivez et gérez les réceptions de matières
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-24 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M5 7 3 5"></path>
                <path d="M9 5 5 9"></path>
                <path d="m13 5-5 5"></path>
                <path d="m17 5-9 9"></path>
                <path d="M21 5h-4l-7 7"></path>
                <path d="M21 9v4l-7 7"></path>
                <path d="m21 17-4 4"></path>
                <path d="m21 21-9-9"></path>
                <path d="M9 21H5l7-7"></path>
                <path d="M3 21h4l5-5"></path>
                <path d="m3 17 4-4"></path>
                <path d="m3 13 9 9"></path>
              </svg>
            </div>
            <div className="mt-4">
              <a href="/receptions" className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full">
                Gérer les réceptions
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Carte Références Matières */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Références Matières</CardTitle>
            <CardDescription>
              Consultez le catalogue des matières
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-24 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                <line x1="3" y1="9" x2="21" y2="9"></line>
                <line x1="3" y1="15" x2="21" y2="15"></line>
                <line x1="9" y1="3" x2="9" y2="21"></line>
                <line x1="15" y1="3" x2="15" y2="21"></line>
              </svg>
            </div>
            <div className="mt-4">
              <a href="/matieres" className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full">
                Voir les références
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
