# Speaker Notes

## Slide 1: Sports Analytics Dashboard & Match Outcome Prediction
Good morning. This project is a sports analytics platform focused on football match analysis and prediction. It combines real match data, machine learning, interactive dashboards, and a presentation-ready user experience. The goal is to show how data can support better football insight, not just display raw statistics.

## Slide 2: Sports analytics turns match records into decisions
Sports analytics is important because football performance depends on many connected signals. A team can look strong in one match but weak across a longer trend. Machine learning helps combine those signals, while a dashboard makes the results easy to inspect and explain.

## Slide 3: Prediction is difficult without a structured system
The problem is that football information is spread across different sources. Without a structured system, it is hard to compare teams consistently or explain why one outcome is more likely than another. This project addresses that by combining data ingestion, feature engineering, model prediction, and clear explanation.

## Slide 4: The project builds a complete football intelligence workflow
The objectives are practical. The app must load real football data, compare teams, train a model, and present predictions clearly. It also needs to remain usable without API keys, which is important for a university submission and live presentation.

## Slide 5: The architecture connects data, modeling, and dashboard delivery
The architecture starts with verified datasets and cached public sources. The data is cleaned and transformed into features such as recent form, goals, defense rating, and team strength. Those features feed the model, and Streamlit presents the analysis and predictions.

## Slide 6: The dataset contains 684 real match records
The dataset currently contains 684 real match rows and 23 real clubs. It is sourced from the OpenFootball public Premier League files and then cached locally. This gives the project a reliable free mode while still allowing API expansion.

## Slide 7: Visual analytics reveals form and outcome patterns
The visualization page is used to understand the dataset before trusting a model. It includes distributions, correlations, boxplots, and filters. These views help identify whether features such as team strength and scoring trends relate to match outcomes.

## Slide 8: The trained model is Logistic Regression
The selected model in the saved bundle is Logistic Regression. The pipeline compares multiple classifiers and stores the best model with its metrics and feature importance. The purpose is not only prediction, but also explainability.

## Slide 9: Match prediction uses real teams and visible confidence
The Match Prediction page no longer uses fictional teams. It supports verified real leagues and teams, uses live APIs when keys are available, and falls back to public or cached sources. The result includes probability, confidence, and an explanation.

## Slide 10: World Cup prediction uses a transparent strength index
The World Cup page uses a transparent formula. Official senior wins carry the highest value, draws show stability, friendlies carry lower confidence, and youth signals represent the future pipeline. This gives an interpretable team strength index.

## Slide 11: The website is the demonstration environment
The final presentation can be delivered directly inside the application. The website itself is the demonstration environment, with pages for data, analytics, comparison, prediction, model performance, and project explanation.

## Slide 12: Model results are measurable and transparent
The model results are reported openly. Accuracy, precision, recall, and F1 score are shown so the audience can understand model quality. The performance page also includes confusion matrix, ROC curve, model comparison, and feature importance.

## Slide 13: The hardest parts were reliability and realism
The main challenges were practical engineering challenges. APIs may fail or require keys, so the app needs caching and verified fallback data. Another challenge was ensuring the prediction system remains realistic and does not invent teams or fixtures.

## Slide 14: The next version can expand into live football intelligence
Future improvements would make the system more powerful. Live standings, injuries, transfers, expected goals, and mobile access would make it closer to a professional sports intelligence product.

## Slide 15: The platform proves the full analytics lifecycle
To conclude, this project proves a full analytics lifecycle. It starts from real data, transforms that data into features, trains and evaluates a model, and delivers the result through a polished dashboard. Thank you. I am ready for questions.
