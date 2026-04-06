Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

Asa: A Seven-Method Forensic Data Integrity Screener for Clinical Trial Datasets

Can statistical forensic methods reliably detect data fabrication in clinical trial datasets through a single accessible browser-based screening tool? We consolidated seven complementary forensic methods into a browser screener validated against 85 test cases covering fabricated, genuine, and boundary-condition datasets. Asa implements Benford’s law, GRIM and GRIMMER granularity tests, SPRITE stochastic reconstruction, terminal digit analysis, variance ratio tests, and Kolmogorov-Smirnov distribution assessment, each producing an independent risk score from zero to one hundred. The composite integrity score achieved sensitivity and specificity of 100 percent (95% CI 95.7 to 100 percent) for fabrication detection across all 85 validation test cases in the suite. Per-study methods identified impossible mean-sample-size combinations in fabricated datasets, while dataset-level methods flagged distributional anomalies across broader study collections. A multi-method forensic approach substantially reduces false accusation risk compared with reliance on any single statistical test. The tool is limited to summary-level data and cannot detect sophisticated fabrication that preserves all tested statistical properties.

Outside Notes

Type: methods
Primary estimand: Composite forensic integrity score (0-100)
App: Asa v2.0
Data: 85 test cases: fabricated, genuine, and boundary-condition datasets
Code: https://github.com/mahmood726-cyber/asa
Version: 2.0
Certainty: moderate
Validation: DRAFT

References

1. Carlisle JB. Data fabrication and other reasons for non-random sampling in 5087 randomised, controlled trials in anaesthetic and general medical journals. Anaesthesia. 2017;72(8):944-952.
2. Brown NJL, Heathers JAJ. The GRIM test: a simple technique detects numerous anomalies in the reporting of results in psychology. Soc Psychol Personal Sci. 2017;8(4):363-369.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
