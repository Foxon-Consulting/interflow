import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { PageContainer } from "@/components/layouts/page-container";
import { QueryProvider } from "@/providers/query-provider";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Tableau de bord multionglets",
  description: "Application de visualisation de données avec interface à onglets",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.variable} font-sans`}>
        <QueryProvider>
          <PageContainer>{children}</PageContainer>
        </QueryProvider>
      </body>
    </html>
  );
}
