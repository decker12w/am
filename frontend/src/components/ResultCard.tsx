import { Home, TrendingUp, Loader2, Sparkles, Info, BarChart3 } from "lucide-react";

export type ImpactFactor = {
  label: string;
  value: number; // R$ contribution (can be negative)
  weight: number; // 0-100 visual width
};

export type PredictionResult = {
  price: number;
  min: number;
  max: number;
  marginPct: number;
  factors: ImpactFactor[];
};

const formatBRL = (n: number) =>
  n.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });

const formatBRLSigned = (n: number) => (n >= 0 ? `+${formatBRL(n)}` : `-${formatBRL(Math.abs(n))}`);

type Props = {
  loading: boolean;
  result: PredictionResult | null;
};

export function ResultCard({ loading, result }: Props) {
  return (
    <div
      className="relative overflow-hidden rounded-2xl border border-border p-5 shadow-[var(--shadow-card)] sm:p-7"
      style={{ background: "var(--gradient-hero)" }}
    >
      <div
        className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full opacity-30 blur-3xl"
        style={{ background: "var(--gradient-primary)" }}
      />

      <div className="relative">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-primary">
              <Sparkles className="h-3 w-3" />
              Previsão ML
            </p>
            <h2 className="mt-1 text-lg font-bold tracking-tight text-foreground sm:text-xl">
              Resultado da estimativa
            </h2>
          </div>
        </div>

        {loading && <LoadingState />}
        {!loading && !result && <EmptyState />}
        {!loading && result && <ResultState result={result} />}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-2xl bg-card shadow-md">
        <Home className="h-10 w-10 text-primary/60" strokeWidth={1.5} />
      </div>
      <h3 className="text-base font-semibold text-foreground">Aguardando dados do imóvel</h3>
      <p className="mt-2 max-w-xs text-sm text-muted-foreground">
        Preencha o formulário ao lado e clique em <span className="font-semibold">Calcular</span> para
        ver a previsão do aluguel.
      </p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="relative mb-4 flex h-20 w-20 items-center justify-center">
        <div
          className="absolute inset-0 rounded-2xl opacity-20 blur-xl"
          style={{ background: "var(--gradient-primary)" }}
        />
        <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl bg-card shadow-md">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
        </div>
      </div>
      <h3 className="text-base font-semibold text-foreground">Processando dados...</h3>
      <p className="mt-2 max-w-xs text-sm text-muted-foreground">
        Nosso modelo está analisando milhares de imóveis comparáveis em São Carlos.
      </p>
      <div className="mt-6 flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-8 animate-pulse rounded-full bg-primary/40"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}

function ResultState({ result }: { result: PredictionResult }) {
  const formatBRL2 = (n: number) =>
    n.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });

  return (
    <div>
      <div className="rounded-xl border border-border bg-card/60 p-5 backdrop-blur-sm">
        <p className="text-xs font-medium text-muted-foreground">Aluguel mensal estimado</p>
        <div className="mt-1 flex items-baseline gap-1">
          <span
            className="bg-clip-text text-4xl font-extrabold tracking-tight text-transparent sm:text-5xl"
            style={{ backgroundImage: "var(--gradient-primary)" }}
          >
            {formatBRL2(result.price)}
          </span>
          <span className="text-sm font-medium text-muted-foreground">/mês</span>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-semibold text-primary">
            <TrendingUp className="h-3 w-3" />
            Margem de erro: ± {result.marginPct}%
          </span>
          <span className="text-xs text-muted-foreground">
            Faixa: {formatBRL2(result.min)} – {formatBRL2(result.max)}
          </span>
        </div>
      </div>

      <div className="mt-5">
        <p className="mb-3 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          <BarChart3 className="h-3.5 w-3.5" />
          Fatores de impacto
        </p>
        <ul className="space-y-2.5">
          {result.factors.map((f) => {
            const positive = f.value >= 0;
            return (
              <li key={f.label}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">{f.label}</span>
                  <span
                    className={
                      positive
                        ? "font-semibold text-primary tabular-nums"
                        : "font-semibold text-destructive tabular-nums"
                    }
                  >
                    {formatBRLSigned(f.value)}
                  </span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${Math.min(100, Math.max(8, f.weight))}%`,
                      background: positive ? "var(--gradient-primary)" : "var(--color-destructive)",
                    }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="mt-5 flex items-start gap-2 rounded-lg border border-border bg-muted/40 p-3">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          Estimativa baseada em dados de mercado de São Carlos – SP. Não substitui avaliação
          profissional.
        </p>
      </div>
    </div>
  );
}
