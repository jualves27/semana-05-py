import csv
import re

# 1. EXCEÇÃO PERSONALIZADA (Herdando de Exception)

class FormatoInvalidoError(Exception):
    """Exceção lançada quando um campo ou regra de negócio é inválido."""
    pass


# 2. VALIDAÇÕES COM EXPRESSÕES REGULARES (REGEX)

def validar_email(email: str) -> bool:
    # Metacaracteres: ^, \w, \., -, +, @, $
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(padrao, email.strip()))


def validar_cpf(cpf: str) -> bool:
    # Metacaracteres: ^, \d, \., -, $
    padrao = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
    return bool(re.match(padrao, cpf.strip()))


def validar_telefone(telefone: str) -> bool:
    # Metacaracteres: ^, \(, \d, \), \s, -, $
    padrao = r"^\(\d{2}\)\s9\d{4}-\d{4}$"
    return bool(re.match(padrao, telefone.strip()))


def validar_data(data: str) -> bool:
    # Metacaracteres: ^, \d, /, $
    padrao = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
    return bool(re.match(padrao, data.strip()))


# 3. MANIPULAÇÃO DE ARQUIVO E TRATAMENTO DE EXCEÇÕES

def processar_sistema_dados(caminho_arquivo: str):
    registros_validos = []
    registros_invalidos = []

    print("INICIANDO PROCESSAMENTO DE DADOS (PYTHON)\n")

    try:
        # Abertura segura com with open() e encoding utf-8
        with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)

            for num_linha, linha in enumerate(leitor, start=2):
                erros_linha = []

                try:
                    # Captura de KeyError (se alguma coluna obrigatória faltar no arquivo)
                    email = linha["email"]
                    cpf = linha["cpf"]
                    telefone = linha["telefone"]
                    data = linha["data"]
                    
                    # Exemplo de captura de ValueError (se houver campo numérico como ID/Idade)
                    if "idade" in linha:
                        idade = int(linha["idade"])  # Lança ValueError se não for número
                        if idade < 0 or idade > 120:
                            raise FormatoInvalidoError(f"Idade fora do intervalo permitido: {idade}")

                    # Validações com Regex
                    if not validar_email(email):
                        erros_linha.append("E-mail com formato inválido")

                    if not validar_cpf(cpf):
                        erros_linha.append("CPF inválido (esperado: XXX.XXX.XXX-XX)")

                    if not validar_telefone(telefone):
                        erros_linha.append("Telefone inválido (esperado: (XX) 9XXXX-XXXX)")

                    if not validar_data(data):
                        erros_linha.append("Data inválida (esperada: DD/MM/AAAA)")

                except KeyError as e:
                    erros_linha.append(f"Coluna ausente no CSV: {e}")
                except ValueError:
                    erros_linha.append("Falha de conversão numérica (ValueError)")
                except FormatoInvalidoError as e:
                    erros_linha.append(f"Regra de negócio violada: {e}")

                # Separação dos registros
                if not erros_linha:
                    registros_validos.append(linha)
                else:
                    nome_registro = linha.get("nome", f"Registro da linha {num_linha}")
                    registros_invalidos.append({
                        "linha": num_linha,
                        "nome": nome_registro,
                        "motivos": "; ".join(erros_linha)
                    })

    # Tratamento de erro de arquivo inexistente
    except FileNotFoundError:
        print(f"[ERRO CRÍTICO] O arquivo '{caminho_arquivo}' não existe ou não foi encontrado.")
    except Exception as e:
        print(f"[ERRO INESPERADO] Ocorreu uma exceção não tratada: {e}")
    else:
        # Bloco ELSE: executa somente se a leitura do arquivo correu sem exceções críticas
        gerar_relatorio(registros_validos, registros_invalidos)
    finally:
        # Bloco FINALLY: sempre executado ao final
        print("\n--- PROCESSAMENTO FINALIZADO ---")


# 4. RELATÓRIO FORMATADO COM F-STRINGS
def gerar_relatorio(validos: list, invalidos: list):
    total = len(validos) + len(invalidos)
    percentual_sucesso = (len(validos) / total * 100) if total > 0 else 0

    print("         RELATÓRIO FINAL DE ANÁLISE       ")
    print(f"Total de Registros Analisados : {total}")
    print(f"Registros Válidos            : {len(validos)}")
    print(f"Registros Inválidos          : {len(invalidos)}")
    print(f"Taxa de Aprovação            : {percentual_sucesso:.2f}%\n")

    if validos:
        print(" REGISTROS VÁLIDOS ")
        for item in validos:
            nome = item.get("nome", "Sem Nome")
            print(f"✔ [Aprovado] {nome} | Email: {item['email']} | CPF: {item['cpf']}")

    if invalidos:
        print("\n REGISTROS INVÁLIDOS")
        for item in invalidos:
            print(f"✖ [Linha {item['linha']}] {item['nome']}: {item['motivos']}")


if __name__ == "__main__":
    processar_sistema_dados("dados.csv")