export interface Region {
  start: number;
  end: number;
  length: number;
  mean_score: number;
  gene: string;
}

export interface AnalysisData {
  meta: {
    title: string;
    query: string;
    generated: string;
  };
  stats: {
    fetched: number;
    removedShort: number;
    removedAmbiguous: number;
    removedDuplicate: number;
    finalCleaned: number;
    alignmentSequences: number;
    alignmentLength: number;
  };
  conservation: { position: number; score: number }[];
  conservedRegions: Region[];
  variableRegions: Region[];
  variableRegionsNote: string;
  lengthDistribution: { range: string; count: number }[];
  lengthStats: { min: number; max: number; mean: number };
  sampleSequences: { id: string; length: number }[];
  genes: { name: string; start: number; end: number; role: string }[];
  thresholds: {
    conserved: number;
    variable: number;
    minRegionLength: number;
  };
}
