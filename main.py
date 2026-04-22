# main.py
import os
from config import Config
from engine_3d import ThreeDEngine
from payment_manager import PaymentManager
from knowledge_extractor import KnowledgeExtractor
from error_handler import ErrorHandler
from utils import LoggerSetup
def main():
    logger = LoggerSetup.setup_logger()
    error_handler = ErrorHandler(logger)
    config = Config(".env")
    try:
        logger.info("Initializing 3D Engine...")
        engine = ThreeDEngine(config)
        logger.info("Loading payment manager...")
        payment = PaymentManager(config)
        logger.info("Preparing knowledge extractor...")
        extractor = KnowledgeExtractor(config)
        logger.info("Starting main loop...")
        while True:
            user_input = input("Enter command (or 'exit' to quit): ").strip()
            if user_input.lower() == "exit":
                logger.info("Exiting application.")
                break
                try:
                    if user_input.startswith("create_model"):
                        video_path = user_input.split(" ")[1]
                        logger.info(f"Creating 3D model from video: {video_path}")
                        model = engine.create_model_from_video(video_path)
                        logger.info("Model created successfully.")
                    elif user_input.startswith("extract_knowledge"):
                        source = user_input.split(" ")[1]
                        logger.info(f"Extracting knowledge from: {source}")
                        data = extractor.extract(source)
                        logger.info(f"Extracted data: {data}")
                    elif user_input.startswith("process_payment"):
                        amount = float(user_input.split(" ")[1])
                        logger.info(f"Processing payment of amount: {amount}")
                        payment.process(amount)
                        logger.info("Payment processed successfully.")
                    else:
                        logger.warning("Unknown command received.")
                        print("Unknown command. Try again.")
                    except Exception as e:
                        error_handler.handle(e)
                    except Exception as main_e:
                        error_handler.handle(main_e)
                    finally:
                        logger.info("Application terminated.")
                        if __name__ == "__main__":
                            main()
