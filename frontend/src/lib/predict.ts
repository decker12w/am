import type { PropertyData } from "@/components/PredictionForm";
import type { PredictionResult, ImpactFactor } from "@/components/ResultCard";

const neighborhoodMultiplier: Record<string, number> = {
  centro: 1.0,
  "cidade-universitaria": 1.18,
  "santa-felicia": 1.22,
  "vila-prado": 0.92,
  "jardim-paulista": 1.1,
  "parque-faber": 1.28,
};

const neighborhoodLabel: Record<string, string> = {
  centro: "Centro",
  "cidade-universitaria": "Cidade Universitária",
  "santa-felicia": "Santa Felícia",
  "vila-prado": "Vila Prado",
  "jardim-paulista": "Jardim Paulista",
  "parque-faber": "Parque Faber",
};

const typeBase: Record<string, number> = {
  apartment: 1500,
  house: 1800,
  studio: 1100,
};

export function mockPredict(data: PropertyData): PredictionResult {
  const base = typeBase[data.type] ?? 1500;
  const areaContribution = data.area * 22;
  const neighMult = neighborhoodMultiplier[data.neighborhood] ?? 1;
  const locationContribution = base * (neighMult - 1);
  const bedroomsContribution = data.bedrooms * 180;
  const bathroomsContribution = data.bathrooms * 140;
  const parkingContribution = data.parking * 220;
  const furnishedContribution = data.furnished ? 450 : 0;
  const leisureContribution = data.leisureArea ? 280 : 0;
  const securityContribution = data.security ? 210 : 0;

  const subtotal =
    base +
    areaContribution +
    locationContribution +
    bedroomsContribution +
    bathroomsContribution +
    parkingContribution +
    furnishedContribution +
    leisureContribution +
    securityContribution;

  // round to nearest 10
  const price = Math.round(subtotal / 10) * 10;
  const marginPct = 5;
  const min = Math.round((price * (1 - marginPct / 100)) / 10) * 10;
  const max = Math.round((price * (1 + marginPct / 100)) / 10) * 10;

  const rawFactors: { label: string; value: number }[] = [
    { label: `Localização (${neighborhoodLabel[data.neighborhood]})`, value: locationContribution },
    { label: `Área útil (${data.area} m²)`, value: areaContribution },
    { label: `${data.bedrooms} quarto${data.bedrooms !== 1 ? "s" : ""}`, value: bedroomsContribution },
    { label: `${data.parking} vaga${data.parking !== 1 ? "s" : ""} de garagem`, value: parkingContribution },
    {
      label: `${data.bathrooms} banheiro${data.bathrooms !== 1 ? "s" : ""}`,
      value: bathroomsContribution,
    },
  ];

  if (data.furnished) rawFactors.push({ label: "Mobiliado", value: furnishedContribution });
  if (data.leisureArea) rawFactors.push({ label: "Área de lazer", value: leisureContribution });
  if (data.security) rawFactors.push({ label: "Segurança 24h", value: securityContribution });

  const maxAbs = Math.max(...rawFactors.map((f) => Math.abs(f.value)), 1);
  const factors: ImpactFactor[] = rawFactors
    .filter((f) => f.value !== 0)
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 6)
    .map((f) => ({ ...f, weight: (Math.abs(f.value) / maxAbs) * 100 }));

  return { price, min, max, marginPct, factors };
}
