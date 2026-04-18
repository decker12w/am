import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PredictionForm, type PropertyData } from "@/components/PredictionForm";
import { ResultCard, type PredictionResult } from "@/components/ResultCard";
import { mockPredict } from "@/lib/predict";
import { Brain, ShieldCheck, Zap } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "RentIQ — Previsão inteligente de aluguel em São Carlos - SP" },
      {
        name: "description",
        content:
          "Calcule o valor justo de aluguel do seu imóvel em São Carlos com Machine Learning. Previsão precisa baseada em dados reais do mercado.",
      },
      { property: "og:title", content: "RentIQ — Previsão inteligente de aluguel" },
      {
        property: "og:description",
        content: "Plataforma com Machine Learning para prever aluguéis em São Carlos - SP.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);

  const handleSubmit = (data: PropertyData) => {
    setLoading(true);
    setResult(null);
    setTimeout(() => {
      setResult(mockPredict(data));
      setLoading(false);
    }, 1400);
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />

      <main className="flex-1">
        <section className="relative overflow-hidden">
          <div
            className="absolute inset-0 -z-10"
            style={{ background: "var(--gradient-hero)" }}
          />
          <div
            className="absolute -top-40 left-1/2 -z-10 h-96 w-[800px] -translate-x-1/2 rounded-full opacity-20 blur-3xl"
            style={{ background: "var(--gradient-primary)" }}
          />

          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
            <div className="mx-auto max-w-3xl text-center">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-primary">
                <Brain className="h-3 w-3" />
                Powered by Machine Learning
              </span>
              <h1 className="mt-4 text-3xl font-extrabold leading-tight tracking-tight text-foreground sm:text-4xl lg:text-5xl">
                Descubra o valor justo do{" "}
                <span
                  className="bg-clip-text text-transparent"
                  style={{ backgroundImage: "var(--gradient-primary)" }}
                >
                  seu aluguel
                </span>{" "}
                em segundos
              </h1>
              <p className="mt-4 text-base text-muted-foreground sm:text-lg">
                Previsão precisa baseada em dados reais do mercado imobiliário de São Carlos – SP.
              </p>

              <div className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1.5">
                  <Zap className="h-3.5 w-3.5 text-primary" /> Resultado instantâneo
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5 text-primary" /> Modelo validado
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Brain className="h-3.5 w-3.5 text-primary" /> IA explicável
                </span>
              </div>
            </div>

            <div className="mx-auto mt-10 grid max-w-6xl grid-cols-1 gap-6 lg:grid-cols-2">
              <PredictionForm onSubmit={handleSubmit} loading={loading} />
              <div className="lg:sticky lg:top-24 lg:self-start">
                <ResultCard loading={loading} result={result} />
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
