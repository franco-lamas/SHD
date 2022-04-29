from SHD import SHD

host = 265#Mismos numeros de broker que PyHomeBroker
dni = ""
user = ""
password = ""
comitente=#Numero de comitente, no pude traerlo automatico


hb=SHD(host,dni,user,password)

print(hb.get_bluechips("48hs"))#Parametros: 48hs,24hs,spot
print(hb.get_MERVAL())#Sin paramentros, trae los indices BYMA
print(hb.account(comitente))#Trae la tenencia

