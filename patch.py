import os
import re

with open('experiments/generate_results.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_load = """def load_data(results_dir):
    detailed_csv = os.path.join(results_dir, "comparative_results.csv")
    summary_csv = os.path.join(results_dir, "summary_metrics.csv")

    if not os.path.exists(detailed_csv) or not os.path.exists(summary_csv):
        return None, None

    df_detailed = pd.read_csv(detailed_csv)
    df_summary = pd.read_csv(summary_csv)
    return df_detailed, df_summary"""

new_main = """def main():
    base_results_dir = "experiments/results"
    base_output_dir = "docs/Results"
    
    if not os.path.exists(base_results_dir):
        print("Diretório não existe.")
        return

    datasets = [d for d in os.listdir(base_results_dir) if os.path.isdir(os.path.join(base_results_dir, d))]

    print("=" * 70)
    print("[*] GERANDO VISUALIZAÇÕES GRÁFICAS E TABELAS MULTI-DATASET")
    print("=" * 70)

    for dataset in datasets:
        results_dir = os.path.join(base_results_dir, dataset)
        output_dir = os.path.join(base_output_dir, dataset)
        os.makedirs(output_dir, exist_ok=True)
        
        print("")
        print(f"Processando dataset: {dataset.upper()}")
        
        df_detailed, df_summary = load_data(results_dir)
        if df_summary is None:
            print(f"Resultados incompletos no dataset {dataset}, ignorando.")
            continue

        plot_gms_barchart(df_summary, output_dir)
        plot_pareto_scatter(df_summary, output_dir)
        plot_radar_chart(df_summary, output_dir)
        plot_energy_time_barchart(df_summary, output_dir)
        generate_latex_table(df_summary, output_dir)
        generate_discussion_readme(df_summary, output_dir)

        print(f"[OK] Visualizações do {dataset.upper()} salvas em {output_dir}")

if __name__ == "__main__":
    main()
"""

text = re.sub(r"def load_data\(.*?\):.*?return df_detailed, df_summary", new_load, text, flags=re.DOTALL)
text = re.sub(r"def main\(\):.*", new_main, text, flags=re.DOTALL)

with open('experiments/generate_results.py', 'w', encoding='utf-8') as f:
    f.write(text)
