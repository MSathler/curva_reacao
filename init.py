from trabalho_sistemas import parse_tanque_data
if __name__ == '__main__':
	a = parse_tanque_data(file_name = 'test.csv')
	a.run()
	a.plot()
