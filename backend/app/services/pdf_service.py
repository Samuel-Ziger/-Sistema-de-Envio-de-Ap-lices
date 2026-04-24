"""Extração de dados de PDFs de apólice.

Estratégia:
1. Usa pdfplumber para extrair texto página a página.
2. Aplica regex robustos para CPF, CNPJ e número de apólice.
3. Retorna dict com o que achou (nenhum campo é obrigatório).

Observação: regex de número de apólice varia MUITO entre seguradoras, então
deixamos vários padrões e a chave fica opcional.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pdfplumber


# ====== Regex ======
# CPF: 000.000.000-00  ou  00000000000
RE_CPF = re.compile(r"\b(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})\b")
# CNPJ: 00.000.000/0000-00  ou  00000000000000
RE_CNPJ = re.compile(r"\b(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})\b")

# Apólice: várias variantes comuns em seguradoras brasileiras
RE_APOLICE_PATTERNS = [
    re.compile(r"ap[óo]lice[:\s#nº.]*([A-Z0-9][A-Z0-9\-\./]{4,30})", re.IGNORECASE),
    re.compile(r"n[ºo°]\s*ap[óo]lice[:\s]*([A-Z0-9\-\./]{5,30})", re.IGNORECASE),
    re.compile(r"policy\s*(?:number|no\.?)\s*[:\-]?\s*([A-Z0-9\-\./]{5,30})", re.IGNORECASE),
]


@dataclass
class DadosPDF:
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    numero_apolice: Optional[str] = None
    texto_completo: str = ""

    def as_dict(self) -> dict:
        return {
            "cpf": self.cpf,
            "cnpj": self.cnpj,
            "numero_apolice": self.numero_apolice,
        }


def _limpar_doc(doc: str) -> str:
    return re.sub(r"\D", "", doc)


def extrair_dados(caminho_pdf: str | Path) -> DadosPDF:
    caminho = Path(caminho_pdf)
    if not caminho.exists():
        raise FileNotFoundError(caminho)

    texto = ""
    try:
        with pdfplumber.open(str(caminho)) as pdf:
            partes = []
            for pagina in pdf.pages:
                t = pagina.extract_text() or ""
                partes.append(t)
            texto = "\n".join(partes)
    except Exception as e:
        # PDF pode estar corrompido ou ser imagem. Retorna vazio, deixa caller decidir.
        return DadosPDF(texto_completo=f"[ERRO ao ler PDF: {e}]")

    dados = DadosPDF(texto_completo=texto)

    m_cpf = RE_CPF.search(texto)
    if m_cpf:
        dados.cpf = _limpar_doc(m_cpf.group(1))

    m_cnpj = RE_CNPJ.search(texto)
    if m_cnpj:
        dados.cnpj = _limpar_doc(m_cnpj.group(1))

    for pat in RE_APOLICE_PATTERNS:
        m = pat.search(texto)
        if m:
            dados.numero_apolice = m.group(1).strip().rstrip(".,;:")
            break

    return dados


def formatar_cpf(doc: str) -> str:
    d = _limpar_doc(doc)
    if len(d) != 11:
        return doc
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def formatar_cnpj(doc: str) -> str:
    d = _limpar_doc(doc)
    if len(d) != 14:
        return doc
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
