from pydantic import BaseModel, Field
from openai import OpenAI

receipt_data = """
OTOVO, UNIPESSOAL, LDA. RUA VISCONDE DE SEABRA, 3 - 1o DTO 516920219 1700-421 LISBOA
OTOVO, UNIPESSOAL, LDA.
RUA VISCONDE DE SEABRA, 3 - 1o DTO 1700-421 LISBOA
LISBOA
LUCAS BARBOSA NICOLOSI SOARES 0022
AI SOFTWARE ENGINEER 12074046801
292804768
AGEAS 0010.10.315407
516920219 Original DOurpiglicnadlo
LISBOA
Recibo de Vencimentos
Recibo de Vencimentos Período Dezembro
Data Fecho 31/12/2023 Vencimento 3.339,29
Período Data Fecho Vencimento Venc. / Hora N. Dias Mês:
Faltas Alim.
Cód.
R01 R06 R13 D01 D02 D05
Dezembro 31/12/2023
3.339,29 19,27 18.00
Nome
N.o Mecan. Categoria
N.o Benef.
N.o Contrib. Departamento Seguro
LUCAS BARBOSA NICOLOSI SOARES 0022
AI SOFTWARE ENGINEER 12074046801
292804768
AGEAS 0010.10.315407
Retenção IRS
SDD IRS Retido Total Remun.
Venc. / Hora N. Dias Mês:
19,27 18.00
Nome
N.o Mecan. Categoria
N.o Benef.
N.o Contrib. Departamento Seguro
Turno Data
12-2023 12-2023 12-2023 12-2023 12-2023 12-2023
CDD
SDH
Faltas
Alim. Turno CDH
Retenção IRS
IRS Retido
CDH
Descrição Remunerações Descontos
SDH
SDD
Total Remun.
18.059,57
Descontos
432,14 1.146,00 144,00
CDD
Descrição Remunerações
Vencimento 3.339,29 IHT 589,29
4.825,00 18.059,57
4.825,00
Vencimento 3.339,29 IHT 589,29
Cód. Data
R01 12-2023 R06 12-2023 R13 12-2023 D01 12-2023 D02 12-2023 D05 12-2023
Subsídio Alimentação Cartão Segurança Social
IRS (Venc. 29,18%) (29,18%) Desconto Subsidio Alim. Cartão
144,00
Subsídio Alimentação Cartão Segurança Social
IRS (Venc. 29,18%) (29,18%) Desconto Subsidio Alim. Cartão
144,00
432,14 1.146,00 144,00
Formas de Pagamento: % Remuneração
100,00
Forma de Pagamento Moeda
Formas de Pagamento: % Remuneração
100,00
Forma de Pagamento
Transferência
Moeda
Total
4.072,58 1.722,14 Total Pago ( EUR ) 2.350,44
Total
4.072,58 Total Pago ( EUR )
1.722,14 2.350,44
Declaro que recebi a quantia constante neste recibo,
Obs.
Declaro que recebi a quantia constante neste recibo,
Transferência EUR
EUR
"""

class ReceiptData(BaseModel):
    company_name: str = Field(description="The name of the company.")
    date_of_closure: str = Field(description="The date of closure.")
    amount_paid: float = Field(description="The amount paid ('Total Pago') after taxes.")

client = OpenAI()

completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": """
         You are an extraction engine for receipt data.
         Users will upload the contents of their receipts and you will extract
         the following fields:
         - Company name
         - Date of closure
         - Amount paid
         """},
        {"role": "user", "content": receipt_data},
    ],
    response_format=ReceiptData,
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed)
else:
    print(message.refusal)