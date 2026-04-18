import { Building2, MapPin, ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

const cities = [
  { id: "sao-carlos", name: "São Carlos", state: "SP", available: true },
  { id: "sao-paulo", name: "São Paulo", state: "SP", available: false },
  { id: "campinas", name: "Campinas", state: "SP", available: false },
  { id: "ribeirao-preto", name: "Ribeirão Preto", state: "SP", available: false },
];

export function Header() {
  const [selected, setSelected] = useState(cities[0]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-lg text-primary-foreground shadow-md"
            style={{ background: "var(--gradient-primary)" }}
          >
            <Building2 className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <p className="text-base font-bold tracking-tight text-foreground">RentIQ</p>
            <p className="hidden text-[10px] font-medium uppercase tracking-wider text-muted-foreground sm:block">
              ML Rent Predictor
            </p>
          </div>
        </div>

        <div ref={ref} className="relative">
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium text-foreground shadow-sm transition hover:border-primary/40 hover:shadow-md"
          >
            <MapPin className="h-4 w-4 text-primary" />
            <span className="hidden sm:inline">
              {selected.name} - {selected.state}
            </span>
            <span className="sm:hidden">{selected.state}</span>
            <ChevronDown
              className={cn("h-4 w-4 text-muted-foreground transition-transform", open && "rotate-180")}
            />
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-64 overflow-hidden rounded-xl border border-border bg-popover shadow-xl">
              <div className="border-b border-border bg-muted/40 px-3 py-2">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Selecione a cidade
                </p>
              </div>
              <ul className="max-h-72 overflow-y-auto p-1">
                {cities.map((city) => (
                  <li key={city.id}>
                    <button
                      disabled={!city.available}
                      onClick={() => {
                        if (city.available) {
                          setSelected(city);
                          setOpen(false);
                        }
                      }}
                      className={cn(
                        "flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm transition",
                        city.available
                          ? "hover:bg-accent text-foreground cursor-pointer"
                          : "text-muted-foreground cursor-not-allowed",
                        selected.id === city.id && "bg-accent/60 font-semibold",
                      )}
                    >
                      <span className="flex items-center gap-2">
                        <MapPin className="h-3.5 w-3.5" />
                        {city.name} - {city.state}
                      </span>
                      {!city.available && (
                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-primary">
                          Em breve
                        </span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
