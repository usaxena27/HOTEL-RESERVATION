import os
import pandas as pd
import joblib
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from src.logger import get_logger
from src.custom__exception import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml,load_data
from scipy.stats import randint

import mlflow
import mlflow.sklearn

logger = get_logger(__name__)

class ModelTraining:

    def __init__(self,train_path,test_path,model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        self.params_dist = LIGHTGM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

    def load_and_split_data(self):
        try:
            logger.info("Loading and splitting data")
            train_data = load_data(self.train_path)
            test_data = load_data(self.test_path)

            X_train = train_data.drop(columns='booking_status')
            y_train = train_data['booking_status']

            X_test = test_data.drop(columns='booking_status')
            y_test = test_data['booking_status']

            logger.info("Data loaded and split successfully")
            return X_train, y_train, X_test, y_test

        except Exception as e:
            logger.error(f"Error loading and splitting data: {e}")
            raise CustomException("Error while loading and splitting data", e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initializing our model")
            lgbm_model = lgb.LGBMClassifier(random_state=self.random_search_params["random_state"])
            
            logger.info("Starting our Hyperparameter Tuning")

            random_search = RandomizedSearchCV(
                estimator=lgbm_model,
                param_distributions=self.params_dist,
                n_iter=self.random_search_params['n_iter'],
                cv=self.random_search_params['cv'],
                n_jobs=self.random_search_params['n_jobs'],
                verbose=self.random_search_params['verbose'],
                random_state=self.random_search_params['random_state'],
                scoring=self.random_search_params['scoring']
            )
            
            logger.info("Starting our Model training")

            random_search.fit(X_train, y_train)

            logger.info("Hyperparameter Tuning completed")
            
            best_params = random_search.best_params_
            best_lgbm_model = random_search.best_estimator_

            logger.info(f"Best parameters: {best_params}")

            return best_lgbm_model

        except Exception as e:
            logger.error(f"Error training LightGBM model: {e}")
            raise CustomException("Error while training LightGBM model", e)
        
    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating model")
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average="weighted")
            recall = recall_score(y_test, y_pred, average="weighted")
            f1 = f1_score(y_test, y_pred, average="weighted")

            logger.info(f"Accuracy: {accuracy}")
            logger.info(f"Precision: {precision}")
            logger.info(f"Recall: {recall}")
            logger.info(f"F1 Score: {f1}")

            return {
                "accuracy" : accuracy, 
                "precision" : precision,
                "recall" : recall,
                "f1" : f1
            }
        except Exception as e:
            logger.error(f"Error while evaluating model: {e}")
            raise CustomException("Failed to evaluate model", e)
        
    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            logger.info("Saving the model")
            joblib.dump(model, self.model_output_path)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException("Failed to save model", e)
        
    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Starting our model training")
            
                logger.info("Starting our MLFLOW experimentation")

                logger.info("Logging the training and testing dataset to MLFLOW")
                mlflow.log_artifact(self.train_path , artifact_path="datasets")
                mlflow.log_artifact(self.test_path , artifact_path="datasets")
                
                X_train, y_train, X_test, y_test = self.load_and_split_data()
                best_lgbm_model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(best_lgbm_model, X_test, y_test)
                self.save_model(best_lgbm_model)

                logger.info("Logging the model into MLFLOW")
                mlflow.log_artifact(self.model_output_path)

                logger.info("Logging the model into MLFLOW")

                mlflow.log_params(best_lgbm_model.get_params())
                mlflow.log_metrics(metrics)
                logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error while running model training: {e}")
            raise CustomException("Failed to run model training", e)
        
if __name__ == "__main__":
    trainer = ModelTraining(PROCESSED_TRAIN_DATA_PATH,PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    trainer.run()
