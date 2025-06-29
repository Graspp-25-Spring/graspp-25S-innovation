import pandas as pd
import settings
import data_processor
import visualization
import regression


def main():

    # Run scraper
    print("Starting data scraping...")
    scraper = data_processor.DataScraper(settings.BASE_URLs_scrape, settings.DOWNLOAD_DIR, settings.YEARS_TO_SCRAPE)
    scraper.run_scraper()
    print("Data scraping complete.")

    # Run data cleaning
    print("\nStarting data cleaning...")
    cleaner = data_processor.DataCleaner(settings.DOWNLOAD_DIR, settings.CLEAND_DIR)
    cleaner.clean_all_data()
    print("Data cleaning complete.")
    
    # create panale data
    panel_df, research_dict, patent_dict, labor_dict = data_processor.PanelDataProducer.create_panel_data()
    if panel_df is not None:
        # visualization
        visualization.Plotsproducer.generate_all_visualizations(panel_df, patent_dict)
        # run regression
        regression.run_regressions(panel_df)
        
        print("\n🎉 全ての処理が正常に完了しました。")
    else:
        print("\n❌ パイプラインの実行中にエラーが発生しました。")



if __name__ == "__main__":
    pd.set_option('future.no_silent_downcasting', True)
    main()
