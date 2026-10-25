# Version 2 field map

Reviewed on 2026-10-25. CSO semantics and the agreed denominator changes are recorded below.

| Section | Field | SAPS columns | Denominator | Notes |
| --- | --- | --- | --- | --- |
| Population | Total | T1_1AGETT | T1_1AGETT |  |
| Population | Male | T1_1AGETM | T1_1AGETT |  |
| Population | Female | T1_1AGETF | T1_1AGETT |  |
| Marital status | Single | T1_2SGLT | T1_2T | All ages, as published in SAPS; married includes civil partnerships. Approved change from requested 15+ base. |
| Marital status | Married (incl. civil partnership) | T1_2MART | T1_2T | All ages, as published in SAPS; married includes civil partnerships. Approved change from requested 15+ base. |
| Marital status | Separated | T1_2SEPT | T1_2T | All ages, as published in SAPS; married includes civil partnerships. Approved change from requested 15+ base. |
| Marital status | Divorced | T1_2DIVT | T1_2T | All ages, as published in SAPS; married includes civil partnerships. Approved change from requested 15+ base. |
| Marital status | Widowed | T1_2WIDT | T1_2T | All ages, as published in SAPS; married includes civil partnerships. Approved change from requested 15+ base. |
| Irish language | Can speak Irish | T3_1YES | T3_1T |  |
| Nationality | Irish (citizenship) | T2_1IEC | T2_1TC | Citizenship, not native-born. Label needs clarification. |
| Nationality | Non-Irish citizenship | T2_1UKC, T2_1PLC, T2_1INC, T2_1EUC, T2_1RWC | T2_1TC | Sum of five published non-Irish citizenship categories; not stated is excluded from the numerator. |
| Religion | Catholic | T2_4CA | T2_4T |  |
| Religion | No religion | T2_4NR | T2_4T |  |
| Religion | Other religion | T2_4OR | T2_4T |  |
| Health | General health very good | T12_3_VGT | T12_3_TT |  |
| Carers | Provides unpaid care | T12_2_T | T1_1AGETT | Total population denominator, as approved. |
| Smoking | Daily smokers | null | T12_4_T | Published SAPS combines all smokers; not daily-only. |
| Disability | People with a disability | T12_1_T | T1_1AGETT | Total population denominator, as approved. |
| Economic status | At work | T8_1_WT | T8_1_TT |  |
| Economic status | Retired | T8_1_RT | T8_1_TT |  |
| Economic status | Students | T8_1_ST | T8_1_TT |  |
| Economic status | Unemployed (incl. first-job seekers) | T8_1_LFFJT, T8_1_STUT, T8_1_LTUT | T8_1_TT | Sum of CSO first-job, short-term and long-term unemployed categories, as approved. |
| Remote work | Works mainly at or from home | T11_1_WMFHW | T11_1_TW |  |
| Age | Age 0–4 | T1_1AGE0T, T1_1AGE1T, T1_1AGE2T, T1_1AGE3T, T1_1AGE4T | T1_1AGETT |  |
| Age | Age 20–24 | T1_1AGE20_24T | T1_1AGETT |  |
| Age | Age 50–54 | T1_1AGE50_54T | T1_1AGETT |  |
| Age | Age 75+ | T1_1AGE75_79T, T1_1AGE80_84T, T1_1AGEGE_85T | T1_1AGETT |  |
| Families | Married couples (no children) | null | T4_1_TF | SAPS family tables do not distinguish married and cohabiting couples. Household composition rows count households, not families; no substitution. |
| Families | Married with children | null | T4_1_TF | SAPS family tables do not distinguish married and cohabiting couples. Household composition rows count households, not families; no substitution. |
| Families | Cohabiting couples | null | T4_1_TF | SAPS family tables do not distinguish married and cohabiting couples. Household composition rows count households, not families; no substitution. |
| Families | One-parent families | T4_3FOPMCT, T4_3FOPFCT | T4_1_TF | Sum of CSO mother and father one-parent family totals. |
| Households | Single-occupant households | T5_1OP_H | T5_1T_H |  |
| Tenure | Owned with mortgage | T6_3_OMLH | T6_3_TH |  |
| Tenure | Owned outright | T6_3_OOH | T6_3_TH |  |
| Tenure | Rented: private landlord | T6_3_RPLH | T6_3_TH |  |
| Tenure | Rented: local authority | T6_3_RLAH | T6_3_TH |  |
| Tenure | Rented: voluntary/co-operative | T6_3_RVCHBH | T6_3_TH |  |
| Dwellings | Vacant | T6_8_OVD | T6_8_T |  |
| Dwellings | Unoccupied holiday homes | T6_8_UHH | T6_8_T |  |
| Bedrooms | 3 bedrooms | T6_9_3BRH | T6_9_TH |  |
| Bedrooms | 5+ bedrooms | T6_9_GE5BRH | T6_9_TH | GE5 is the terminal bedroom band; glossary description says 5 bedrooms. Code and full partition identify 5+; no higher bedroom band exists. |
| Water | Public mains | T6_6_PM | T6_6_T |  |
| Water | Group schemes / private water | T6_6_GSLA, T6_6_GSP, T6_6_OP | T6_6_T | Includes group schemes with public source, as approved. |
| Heating fuel | Oil | T6_5_OCH | T6_5_T |  |
| Heating fuel | Natural gas | T6_5_NGCH | T6_5_T |  |
| Heating fuel | Electric | T6_5_ECH | T6_5_T |  |
| Heating fuel | Coal (incl. anthracite) | T6_5_CCH | T6_5_T |  |
| Renewable energy | No renewable energy source | T6_10_NORE | T6_10_T |  |
| Smoke alarm | No smoke alarms | T6_11_NOSA | T6_11_T | Published CSO label used, as approved. |
| Internet | Broadband | T15_2_BB | T15_2_T |  |
| Cars | No car | T15_1_NC | T15_1_TC |  |
| Cars | 3+ cars | T15_1_3C, T15_1_GE4C | T15_1_TC |  |
