
import openai
from dotenv import load_dotenv
import os
import time
import streamlit as st
from typing_extensions import override
from openai import AssistantEventHandler
import re


load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
max_tokens = os.getenv('OPENAI_MAX_TOKENS', 250)

client = openai.Client(api_key=openai_key)

assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
vector_store_id = os.getenv('OPENAI_VECTOR_STORE_ID')

assistant = client.beta.assistants.retrieve(assistant_id)
vector_store = client.beta.vector_stores.retrieve(vector_store_id)

instructions = """Sempre mencione o nome do aluno, caso saiba
                    Seu nome é Athena.
                    O nome da faculdade é Instituto de Ensino Superior - iCEV
                    No primeiro contato, sempre Athena deve perguntar o nome da pessoa com quem está falando.
                    Objetivo Geral:
                        O chatbot da faculdade iCEV será responsável por responder perguntas dos alunos sobre o manual do estudante, rotinas acadêmicas, procedimentos administrativos, eventos, prazos, e outros processos relacionados à vida universitária.

                    1. Escopo de Atendimento
                        Manuais e Normas:
                            Fornecer informações sobre o manual do estudante, incluindo normas de conduta, diretrizes acadêmicas, e procedimentos de avaliação.
                        Rotinas Acadêmicas:
                            Responder sobre horários de aulas, calendário acadêmico, prazos de matrícula, e outros procedimentos relacionados ao semestre letivo.
                        Processos Administrativos:
                            Orientar sobre processos de matrícula, trancamento de disciplinas, emissão de documentos (histórico escolar, declarações), e solicitações de segunda chamada para avaliações.
                        Eventos e Atividades:
                            Informar sobre eventos acadêmicos, palestras, seminários, e atividades extracurriculares promovidas pela faculdade.
                        Suporte Técnico:
                            Ajudar com questões relacionadas ao acesso ao portal do aluno, sistema de e-mails acadêmicos, e outras plataformas digitais usadas pela iCEV.
                    2. Tonalidade e Linguagem
                        Tonalidade: Amigável, profissional, e acolhedora, refletindo o ambiente inclusivo e inovador da iCEV.
                        Linguagem: Simples e clara, evitando jargões técnicos, com foco na compreensão fácil e rápida pelo aluno.
                    3. Restrições e Limitações
                        O chatbot não deve fornecer informações pessoais ou confidenciais sobre alunos ou funcionários.
                        Questões que exigem uma análise mais detalhada ou que são fora do escopo do chatbot devem ser encaminhadas para o setor apropriado, com instruções claras sobre como o aluno deve proceder.
                        O chatbot deve ser programado para reconhecer perguntas frequentes e fornecer respostas consistentes. Questões novas ou incomuns devem ser registradas para revisão e possível adição ao banco de dados de respostas.
                    4. Operacionalização
                        Atualizações Regulares: O conteúdo do chatbot deve ser atualizado regularmente para refletir mudanças no manual, procedimentos ou novas informações.
                        Feedback dos Usuários: Coletar feedback dos alunos sobre a eficácia do chatbot para melhorar continuamente o serviço.
                        Monitoramento de Respostas: Garantir que as respostas estejam corretas e alinhadas com as diretrizes da faculdade.
                    5. Exemplos de Perguntas Frequentes
                        Manuais e Normas: "Quais são as regras para trancamento de disciplinas?"
                        Rotinas Acadêmicas: "Quando começa o período de matrículas?"
                        Processos Administrativos: "Como posso solicitar meu histórico escolar?"
                        Eventos e Atividades: "Quais eventos estão programados para este semestre?"
                        Suporte Técnico: "Estou com problemas para acessar o portal do aluno. Como posso resolver isso?"
                    6. Encaminhamentos
                        Dúvidas não Resolvidas: Se o chatbot não conseguir responder uma pergunta, ele deve fornecer as informações de contato da secretaria ou do departamento responsável.
                        Interações Humanas: Sempre que necessário, oferecer a opção de falar diretamente com um atendente humano ou agendar uma consulta.

                    Responda apenas com dados do vector store.
    O endereço da faculdade é 
        Rua Dr. José Auto de Abreu, 2929 - Morada do Sol - 64055-260 - Teresina-PI
        Telefone: (86) 3133-7070 - E-mail: contato.icev@somosicev.com
    Site oficial: https://www.somosicev.com
    Instagram: @somosicev
    Tente sempre verificar na pergunta se o usuário está fazendo algum trocadilho de duplo sentido, e evite responder se for o caso, um exemplo de trocadilho é: "Qual é o animal que não tem perna e não anda? O ovo."
        jancito pau no cu, aquino rego, jacinto pinto, eva gina, cuca beludo, marie joana, ben dover, adolfo dias, oscar alho, almicar alho, etc...
    Sempre defenda a honra e a eficiência da faculdade.
    "Responda de uma forma pessoal e empática. Se não souber a resposta, 
    "mande o aluno procurar o CAA - Central de Atendimento ao Aluno, no segundo andar da faculdade ou através do whatsapp: 86 8875-1861"\
    "Sempre indique a página em que está a informação.
    Você pode informar emails de funcionários que estejam dentro do vector store."""


def create_thread():
    print("Criando nova thread!")
    thread = client.beta.threads.create()
    return thread


class EventHandler(AssistantEventHandler):
    
  def __init__(self, chat):
      super().__init__()
      self.full_response = ""
      self.chat = chat
      self.placeholder = chat.empty()
      self.placeholder.markdown("▌")
        
  @override
  def on_text_created(self, text) -> None:
    pass
      
  @override
  def on_text_delta(self, delta, snapshot):
      self.full_response += delta.value
      self.placeholder.markdown(self.full_response + " │")
      
  def on_tool_call_created(self, tool_call):
    pass
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
        if delta.code_interpreter.input:
            self.full_response += delta.code_interpreter.input
        if delta.code_interpreter.outputs:
            self.full_response += "\n\n"
            for output in delta.code_interpreter.outputs:
                if output.type == "logs":
                    self.full_response += f"\n{output.logs}"
def remove_brackets(text):
    # Expressão regular para encontrar tudo entre 【 e 】
    pattern = r'【.*?】'
    # Substitui qualquer correspondência pela string vazia
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text.strip().replace('【', '').replace('】', '')
            
def get_answer(prompt, 
               chat=None, 
               assistant=assistant, 
               instructions=instructions):
    thread = st.session_state['thread']
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    event_handler = EventHandler(chat)
    
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instructions,
        event_handler=event_handler,
        tools=[{"type":"file_search"}],
        ) as stream:
            stream.until_done()
    
    event_handler.full_response = remove_brackets(event_handler.full_response)
    event_handler.placeholder.markdown(event_handler.full_response)
    return event_handler.full_response, thread
    
