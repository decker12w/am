import { useState, useEffect } from "react";
import {
  Home,
  MapPin,
  Ruler,
  BedDouble,
  Bath,
  Car,
  Calculator,
  Loader2,
  Minus,
  Plus,
} from "lucide-react";
import { api, type Neighborhood } from "@/lib/api";

export type PropertyData = {
  type: string;
  neighborhood_id: string;
  area: number;
  bedrooms: number;
  bathrooms: number;
  parking: number;
};

const propertyTypes = [
  { value: "apartment", label: "Apartamento" },
  { value: "house", label: "Casa" },
  { value: "studio", label: "Studio / Kitnet" },
];

type Props = {
  onSubmit: (data: PropertyData) => void;
  loading: boolean;
};

function Stepper({
  value,
  onChange,
  min = 0,
  max = 10,
}: {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
}) {
  return (
    <div className="flex items-center rounded-lg border border-border bg-card">
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        className="flex h-10 w-10 items-center justify-center text-muted-foreground transition hover:bg-accent hover:text-primary disabled:opacity-40"
        disabled={value <= min}
      >
        <Minus className="h-4 w-4" />
      </button>
      <span className="flex-1 text-center text-base font-semibold text-foreground tabular-nums">
        {value}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(max, value + 1))}
        className="flex h-10 w-10 items-center justify-center text-muted-foreground transition hover:bg-accent hover:text-primary disabled:opacity-40"
        disabled={value >= max}
      >
        <Plus className="h-4 w-4" />
      </button>
    </div>
  );
}

function FieldLabel({ icon: Icon, children }: { icon: React.ElementType; children: React.ReactNode }) {
  return (
    <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      <Icon className="h-3.5 w-3.5" />
      {children}
    </label>
  );
}

export function PredictionForm({ onSubmit, loading }: Props) {
  const [neighborhoods, setNeighborhoods] = useState<Neighborhood[]>([]);
  const [data, setData] = useState<PropertyData>({
    type: "apartment",
    neighborhood_id: "",
    area: 75,
    bedrooms: 2,
    bathrooms: 1,
    parking: 1,
  });

  useEffect(() => {
    api.neighborhoods().then((list) => {
      setNeighborhoods(list);
      if (list.length > 0 && !data.neighborhood_id) {
        setData((d) => ({ ...d, neighborhood_id: list[0].id }));
      }
    });
  }, []);

  const update = <K extends keyof PropertyData>(key: K, value: PropertyData[K]) =>
    setData((d) => ({ ...d, [key]: value }));

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(data);
      }}
      className="rounded-2xl border border-border bg-card p-5 shadow-(--shadow-card) sm:p-7"
    >
      <div className="mb-6">
        <h2 className="text-lg font-bold tracking-tight text-foreground sm:text-xl">
          Dados do imóvel
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Preencha as características para receber a previsão.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <FieldLabel icon={Home}>Tipo de imóvel</FieldLabel>
          <select
            value={data.type}
            onChange={(e) => update("type", e.target.value)}
            className="h-10 w-full rounded-lg border border-input bg-card px-3 text-sm text-foreground shadow-sm transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/30"
          >
            {propertyTypes.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <FieldLabel icon={MapPin}>Bairro</FieldLabel>
          <select
            value={data.neighborhood_id}
            onChange={(e) => update("neighborhood_id", e.target.value)}
            className="h-10 w-full rounded-lg border border-input bg-card px-3 text-sm text-foreground shadow-sm transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/30"
            disabled={neighborhoods.length === 0}
          >
            {neighborhoods.length === 0 && (
              <option value="">Carregando...</option>
            )}
            {neighborhoods.map((n) => (
              <option key={n.id} value={n.id}>
                {n.name.replace(/\b\w/g, (c) => c.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        <div className="sm:col-span-2">
          <FieldLabel icon={Ruler}>Área útil</FieldLabel>
          <div className="relative">
            <input
              type="number"
              min={10}
              max={2000}
              value={data.area}
              onChange={(e) => update("area", Number(e.target.value))}
              className="h-10 w-full rounded-lg border border-input bg-card px-3 pr-12 text-sm text-foreground shadow-sm transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/30"
            />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-muted-foreground">
              m²
            </span>
          </div>
        </div>

        <div>
          <FieldLabel icon={BedDouble}>Quartos</FieldLabel>
          <Stepper value={data.bedrooms} onChange={(v) => update("bedrooms", v)} max={8} />
        </div>

        <div>
          <FieldLabel icon={Bath}>Banheiros</FieldLabel>
          <Stepper value={data.bathrooms} onChange={(v) => update("bathrooms", v)} min={1} max={6} />
        </div>

        <div className="sm:col-span-2">
          <FieldLabel icon={Car}>Vagas de garagem</FieldLabel>
          <Stepper value={data.parking} onChange={(v) => update("parking", v)} max={6} />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !data.neighborhood_id}
        className="mt-7 flex h-12 w-full items-center justify-center gap-2 rounded-xl text-sm font-semibold text-primary-foreground shadow-(--shadow-elegant) transition hover:opacity-95 active:scale-[0.99] disabled:opacity-70"
        style={{ background: "var(--gradient-primary)" }}
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Calculando previsão...
          </>
        ) : (
          <>
            <Calculator className="h-4 w-4" />
            Calcular previsão de aluguel
          </>
        )}
      </button>
    </form>
  );
}
