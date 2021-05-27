from trabalho_sistemas import parse_tanque_data
if __name__ == '__main__':
	a = parse_tanque_data(file_name = 'pi_3p5_0p08.csv')
	a.run()
	a.plot()
