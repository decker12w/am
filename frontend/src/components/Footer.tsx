import { Building2, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-border bg-card/40">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-6 sm:flex-row sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Building2 className="h-4 w-4 text-primary" />
          <span>
            © {new Date().getFullYear()} <span className="font-semibold text-foreground">RentIQ</span>{" "}
            — Previsão inteligente de aluguéis.
          </span>
        </div>
        <a
          href="#"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-primary transition hover:underline"
        >
          Como funciona o modelo de previsão
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </footer>
  );
}
