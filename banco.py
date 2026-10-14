#DEPOSITO
#SAQUE
#EXTRATO

import streamlit as st

st.title ('NuBank')

print ('Bem vindo ao nuAtendimento, como podemos ajudar?')

senha = 'corinthians'

acessar = st.text_input('Deseja acessar o seu roxinho? s/n ')

saldo = 1000.00

extrato = []

# while acessar == 's':

senha_input = st.text_input('Insira a senha: ')

if st.button('Acessar'):

    if senha_input == senha:

        print ('Acesso autorizado')
        menu = ['', 'Saque', 'Depósito', 'Extrato']
        print (f'''
            1 - {menu[1]}
            2 - {menu[2]}
            3 - {menu[3]}
        ''')
        escolha = int(input('Escolha a operação:'))
        if escolha == 1:
            saque = st.number_input('Digite o valor do saque:')
            saldo = saldo - saque
            st.write('O valor restante em conta é: R$',saldo)
            extrato.append(-saque)
            acessar = st.text_input ('Deseja continuar? s/n ')
        elif escolha == 2:
            deposito = st.number_input('Digite o valor do deposito:')
            saldo = saldo + deposito
            st.write('O novo valor em conta é: R$',saldo)
            extrato.append(deposito)
            acessar = st.text_input ('Deseja continuar? s/n ')
        elif escolha == 3:
            st.write('extrato', extrato)
            acessar = st.text_input ('Deseja continuar? s/n ')

    else:
        print ('Acesso negado') 
# else:
#     print ('Até logo')

