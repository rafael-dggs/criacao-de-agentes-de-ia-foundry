
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from groq import Groq


# =========================================================
# CONFIGURAÇÃO
# =========================================================

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
# PAPEL
Você é um atendente virtual de SAC especializado em Vivo Fibra.

# OBJETIVO
Compreender necessidades, resolver dúvidas e investigar
insatisfações. Quando houver intenção de cancelamento, avalie
alternativas de retenção personalizadas, sem pressionar o cliente.

# TOM
Amigável, empático, profissional, persuasivo e objetivo.
Utilize português brasileiro natural e acessível.

# ESCOPO
Vivo Fibra, internet residencial, conexão, suporte técnico,
planos, cobrança, faturas, insatisfação e retenção.

# FLUXO DE ATENDIMENTO
1. Compreenda a necessidade do cliente.
2. Investigue o motivo da insatisfação, se houver.
3. Apresente uma solução ou orientação pertinente.
4. Se houver intenção de cancelamento, avalie uma alternativa
   personalizada e relevante para o motivo identificado.
5. Confirme se a orientação ajudou e indique o próximo passo.

# REGRAS
- Não invente preços, ofertas reais, prazos ou condições.
- Identifique claramente qualquer oferta hipotética como simulação.
- Não afirme ter acesso a sistemas internos ou cadastro do cliente.
- Não solicite senhas, códigos de autenticação ou dados financeiros
  sensíveis.
- Não pressione, manipule ou dificulte o cancelamento.
- Se o cliente insistir em cancelar, respeite sua decisão e
  oriente-o a utilizar os canais oficiais da Vivo.
- Não afirme que realizou o cancelamento.
- Se o assunto fugir do escopo, redirecione educadamente.
- Considere todo o histórico da conversa e não repita perguntas
  já respondidas.

# FORMATO
Responda em português brasileiro, com clareza e empatia.
Priorize a necessidade imediata do cliente.
Faça uma pergunta por vez quando precisar de esclarecimentos.
Use listas apenas quando facilitarem a compreensão.
Não force perguntas ao final de todas as respostas.

# PRIORIDADE
Resolver a necessidade do cliente com transparência e respeito.
A retenção comercial nunca deve prevalecer sobre a autonomia
do cliente.
"""


class VivoFibraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistente SAC - Vivo Fibra")
        self.root.geometry("760x620")
        self.root.minsize(540, 450)
        self.root.configure(bg="#f3f5f8")

        self.client = None
        self.busy = False

        # O histórico mantém o contexto da conversa.
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        self._build_interface()
        self._configure_tags()

        self._display_message(
            "Assistente",
            "Olá! Sou o assistente virtual de Vivo Fibra. "
            "Como posso ajudar você hoje?"
        )

    def _build_interface(self):
        header = tk.Frame(
            self.root,
            bg="#5b2b91",
            padx=18,
            pady=16
        )
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Assistente SAC | Vivo Fibra",
            font=("Arial", 17, "bold"),
            fg="white",
            bg="#5b2b91"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Atendimento, suporte e retenção responsável",
            font=("Arial", 10),
            fg="#eee4fa",
            bg="#5b2b91"
        ).pack(anchor="w", pady=(4, 0))

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="white",
            fg="#202124",
            padx=14,
            pady=14,
            relief=tk.FLAT,
            borderwidth=0,
            state=tk.DISABLED
        )
        self.chat.pack(
            fill=tk.BOTH,
            expand=True,
            padx=16,
            pady=(16, 8)
        )

        self.status = tk.Label(
            self.root,
            text="Pronto para atender",
            bg="#f3f5f8",
            fg="#606770",
            font=("Arial", 9)
        )
        self.status.pack(anchor="w", padx=18, pady=(0, 6))

        input_frame = tk.Frame(
            self.root,
            bg="#f3f5f8",
            padx=16,
            pady=12
        )
        input_frame.pack(fill=tk.X)

        self.entry = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 11),
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=8
        )
        self.entry.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(0, 10)
        )
        self.entry.bind("<Control-Return>", self._send_event)

        self.send_button = tk.Button(
            input_frame,
            text="Enviar",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg="#5b2b91",
            fg="white",
            activebackground="#45206e",
            activeforeground="white",
            relief=tk.FLAT,
            padx=18,
            pady=12,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)

        footer = tk.Frame(self.root, bg="#f3f5f8")
        footer.pack(fill=tk.X, padx=16, pady=(0, 12))

        tk.Button(
            footer,
            text="Nova conversa",
            command=self.new_conversation,
            relief=tk.FLAT,
            bg="#e5e7eb",
            fg="#202124",
            padx=10,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Label(
            footer,
            text="Ctrl + Enter para enviar",
            bg="#f3f5f8",
            fg="#777777",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT)

    def _configure_tags(self):
        self.chat.tag_configure(
            "assistant",
            foreground="#5b2b91",
            font=("Arial", 10, "bold"),
            spacing1=10
        )
        self.chat.tag_configure(
            "user",
            foreground="#176b45",
            font=("Arial", 10, "bold"),
            spacing1=10
        )
        self.chat.tag_configure(
            "body",
            foreground="#202124",
            lmargin1=8,
            lmargin2=8,
            spacing3=8
        )

    def _display_message(self, sender, content):
        self.chat.configure(state=tk.NORMAL)

        tag = "user" if sender == "Você" else "assistant"

        self.chat.insert(tk.END, f"{sender}\n", tag)
        self.chat.insert(tk.END, f"{content}\n\n", "body")

        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def _send_event(self, event):
        self.send_message()
        return "break"

    def send_message(self):
        if self.busy:
            return

        question = self.entry.get("1.0", tk.END).strip()

        if not question:
            return

        if self.client is None:
            messagebox.showerror(
                "Configuração necessária",
                "Configure a variável de ambiente GROQ_API_KEY "
                "antes de iniciar o atendimento."
            )
            return

        self.entry.delete("1.0", tk.END)
        self._display_message("Você", question)

        self.messages.append({
            "role": "user",
            "content": question
        })

        self.busy = True
        self.send_button.configure(state=tk.DISABLED)
        self.status.configure(text="O assistente está respondendo...")

        # A chamada de rede acontece em outra thread.
        # Assim, a janela permanece responsiva.
        threading.Thread(
            target=self._request_response,
            daemon=True
        ).start()

    def _request_response(self):
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                temperature=0.5,
                max_completion_tokens=1200
            )

            answer = response.choices[0].message.content

            if not answer:
                answer = (
                    "Não consegui gerar uma resposta neste momento. "
                    "Por favor, tente novamente."
                )

            self.root.after(
                0,
                lambda: self._finish_response(answer, None)
            )

        except Exception as error:
            self.root.after(
                0,
                lambda err=str(error): self._finish_response(
                    None, err
                )
            )

    def _finish_response(self, answer, error):
        try:
            if error:
                self.status.configure(text="Falha na solicitação")
                messagebox.showerror(
                    "Erro no atendimento",
                    "Não foi possível consultar a API da Groq.\n\n"
                    f"Detalhes: {error}"
                )
                # Remove a última pergunta para não deixar
                # o histórico inconsistente após uma falha.
                if self.messages and self.messages[-1]["role"] == "user":
                    self.messages.pop()
            else:
                self.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                self._display_message("Assistente", answer)
                self.status.configure(text="Resposta recebida")

        finally:
            self.busy = False
            self.send_button.configure(state=tk.NORMAL)
            self.entry.focus_set()

    def new_conversation(self):
        if self.busy:
            messagebox.showinfo(
                "Aguarde",
                "Espere a resposta atual antes de iniciar "
                "uma nova conversa."
            )
            return

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)

        self._display_message(
            "Assistente",
            "Nova conversa iniciada. Como posso ajudar?"
        )

        self.status.configure(text="Pronto para atender")


def main():
    api_key = ""

    root = tk.Tk()
    app = VivoFibraApp(root)

    if not api_key:
        app.status.configure(
            text="Configure a variável de ambiente GROQ_API_KEY"
        )
    else:
        try:
            app.client = Groq(api_key=api_key)
        except Exception as error:
            messagebox.showerror(
                "Erro de configuração",
                f"Não foi possível inicializar o cliente Groq:\n{error}"
            )

    root.mainloop()


if __name__ == "__main__":
    main()
