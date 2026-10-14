#DEPOSITO
#SAQUE
#EXTRATO

print ('Bem vindo ao nuAtendimento, como podemos ajudar?')

senha = 'corinthians'

acessar = input('Deseja acessar o seu roxinho? s/n ')



saldo = 1000.00

extrato = []

while acessar == 's':

    senha_input = input('Insira a senha: ')
    
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
            saque = float(input('Digite o valor do saque:'))
            saldo = saldo - saque
            print('O valor restante em conta é: R$',saldo)
            extrato.append(-saque)
            acessar = input ('Deseja continuar? s/n ')
        elif escolha == 2:
            deposito = float(input('Digite o valor do deposito:'))
            saldo = saldo + deposito
            print('O novo valor em conta é: R$',saldo)
            extrato.append(deposito)
            acessar = input ('Deseja continuar? s/n ')
        elif escolha == 3:
            print('extrato', extrato)
            acessar = input ('Deseja continuar? s/n ')

    else:
        print ('Acesso negado') 
else:
    print ('Até logo')

