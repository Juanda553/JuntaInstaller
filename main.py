from zipfile import ZipFile
from os import system, getlogin, makedirs, rmdir
from base64 import b64encode
from datetime import datetime
from colorama import *
from tqdm import tqdm
import json, requests, shutil
print(Fore.CYAN + "Iniciando...")
system("cls")

#LOGGER
class ConsLog:
    def log(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.LIGHTBLUE_EX + f'[LOG] {datetimeLog} >> {xyz}')
    
    def logDone(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.LIGHTGREEN_EX + f'[LOG] {datetimeLog} >> {xyz}')

    def error(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.RED + f'[ERROR] {datetimeLog} >> {xyz}')

    def warning(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.YELLOW + f'[WARNING] {datetimeLog} >> {xyz}')

    def tip(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.LIGHTGREEN_EX + f'[TIP] {datetimeLog} >> {xyz}')
    
    def exitMsg():
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        input(Fore.RED + f'[TIP] {datetimeLog} >> Ya puedes cerrar el programa.')
    
    def devTest(xyz):
        ya = datetime.now(); datetimeLog = f"{ya.hour}:{ya.minute}:{ya.second}"
        print(Fore.YELLOW + f'[DEV LOG] {datetimeLog} >> {xyz}')

ConsLog.log("Creando instancias...")
windowsUser = getlogin()
juntaDir = f"C:/Users/{windowsUser}/AppData/Roaming/.jnt"
minecraftDir = f"C:/Users/{windowsUser}/AppData/Roaming/.minecraft"
modpackDownloadDir = f"{juntaDir}/zipPackDown"


# Obtener la version real actual de la Junta
ConsLog.log("Obteniendo datos de la nube de La Junta...")
LaJuntaAPI = requests.get("https://pastebin.com/raw/nj6RWKmF").json()
juntaCloudVersion = LaJuntaAPI["version"]
newJuntaName = LaJuntaAPI["junta"]
newIconURL = LaJuntaAPI["icon"]
newModPack = LaJuntaAPI["modPack"]
minecraftVersion = LaJuntaAPI["forgeVersion"]
modpackName = LaJuntaAPI["modpackName"]
ConsLog.logDone("Datos descargados con exito!")


#convertir imagen en una imagen leible para el launcher de Minecraft
def getDataURL(url):
    try:
        ConsLog.log("Descargando Imagen...")
        # Decargar imagen
        r = requests.get(url, allow_redirects=True)
        open(f'{modpackDownloadDir}/icon.png', 'wb').write(r.content)
        ConsLog.logDone("Imagen descargada.")

        ConsLog.log("Codificando Imagen...")
        # no me acuerdo
        ext = f"{modpackDownloadDir}/icon.png".split('.')[-1]
        dataPrefix = f"data:image/{ext};base64,"

        with open(f"{modpackDownloadDir}/icon.png", "rb") as tempImg:
            img = tempImg.read()
        
        ConsLog.logDone("Imagen Codificada.")
        return dataPrefix + b64encode(img).decode('utf-8')
    except Exception as e:
        ConsLog.error(e)
        return False

def extraerPack():
    try:
        ConsLog.log("Descomprimiendo datos...")
        
        with ZipFile(f"{modpackDownloadDir}/{modpackName}") as zipObject:
            fileCount = len(zipObject.infolist())

        progressBar = tqdm(total=fileCount, unit='archivo', desc='Descomprimiendo')

        with ZipFile(f"{modpackDownloadDir}/{modpackName}") as zipObject:
            for archivo in zipObject.infolist():
                zipObject.extract(archivo, juntaDir)
                progressBar.update(1)

        progressBar.close()


        ConsLog.logDone("Descompresion completa")
            
        # Actualizar los datos locales a la version actual
        ConsLog.log("Actualizando datos locales...")
        with open(f"{modpackDownloadDir}/juntaData.json", "w") as tempFile:
            juntaData = tempFile

            newJuntaData = {"localVersion": juntaCloudVersion}
            json.dump(newJuntaData, juntaData)
        ConsLog.logDone("Actualizado con exito.")
        return True
    except Exception as e:
        ConsLog.error(e)
        return False

def makeLauncherProfile():
    try:
        ConsLog.warning("EL COLOCAR UN VALOR INCORRECTO DE RAM, PUEDE PROVOCAR QUE TU PC LITERALMETE EXPLOTA, ASÍN QUE MUCHO CUIDADO")
        tuRam = int(input("\nCuanta RAM tiene tu PC?\n>> "))
        finalRam = 0

        if tuRam <= 4:
            finalRam = 2
        elif tuRam <= 8:
            finalRam = 4
        elif tuRam <= 12:
            finalRam = 6
        elif tuRam >= 16:
            finalRam = 12

        print("")
        ConsLog.log(f"Iniciando creacion del perfil de La Junta con {tuRam}GB de RAM y con {finalRam}GB de RAM dedicada al juego...")
        with open(f"{minecraftDir}/launcher_profiles.json", "r") as tempProfileFile:
            jsonProfiles = json.load(tempProfileFile)
            jsonProfiles["profiles"]["junta"] = {
                "gameDir": juntaDir,
                "icon": getDataURL(newIconURL),
                "lastVersionId": minecraftVersion,
                "name": newJuntaName,
                "javaArgs": f"-Xmx{finalRam}G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M"
            }

            with open (f"{minecraftDir}/launcher_profiles.json", "w") as tempFile:
                json.dump(jsonProfiles, tempFile, indent=2)
            
            ConsLog.logDone("Perfil creado.")
            return True
    except Exception as e:
        ConsLog.error(e)
        return False

def descargarPack():
    try:
        ConsLog.log("Iniciando descarga del paquete...")

        # saca la url de esa mierda
        repDownload = requests.get(newModPack, stream=True)

        # si sirve el link o no
        if repDownload.status_code == 200:
            totalFileSize = int(repDownload.headers.get('Content-Length', 0))
            barrita = tqdm(total=totalFileSize, unit='MB', unit_scale=True, unit_divisor=1024, desc='Descargando')

            with open(f"{modpackDownloadDir}/{modpackName}", 'wb') as xd:

                for chunk in repDownload.iter_content(chunk_size=128):
                    xd.write(chunk)
                    barrita.update(len(chunk))

            barrita.close()
            ConsLog.logDone(f"Descargado :)")

            ConsLog.log("Creando JSON...")

            with open(f"{modpackDownloadDir}/juntaData.json", "w") as tempFile:
                json.dump({"localVersion": juntaCloudVersion}, tempFile)
                ConsLog.logDone("Creado :)")
                return True
        else:
            ConsLog.error(f"Codigo de estado: {repDownload.status_code}")
            return False


        #gdown.download(newModPack, f"{modpackDownloadDir}/{modpackName}", quiet=False)
    except Exception as e:
        ConsLog.error(e)
        return False

def crearDotJunta():
    try:
        ConsLog.log("Creando directorio...")
        makedirs(juntaDir) # Crea carpeta
        makedirs(modpackDownloadDir)
        ConsLog.logDone("Directorio creado.")

        return True
    except Exception as e:
        ConsLog.error(e)
        return False

def instalacionInicial():
    try:
        ConsLog.log("Limpiando directorio...")
        shutil.rmtree(juntaDir)
        ConsLog.logDone("Directorio limpiado")
    except:
        ConsLog.logDone("Directorio limpiado (No existia)")
    ConsLog.log("Iniciando instalacion de La Junta...")
    if crearDotJunta():
        if descargarPack():
            if makeLauncherProfile():
                if extraerPack():
                    print("")
                    ConsLog.logDone(f"Instalacion terminada!\nPor favor si pusiste una cantidad de RAM incorrecta, reinicia el programa y selecciona reinstalar, para evitar que tu PC explote xD")
                    ConsLog.logDone(f"Listo, ya puedes abrir La Junta {juntaCloudVersion[0]}")
                    ConsLog.tip("Si tienes el launcher de Minecraft abierto, por favor reinicialo. :)")
                    ConsLog.exitMsg()
                else:
                    ConsLog.error("No se pudo descomprimir el paquete de la Junta, manda el error que sale arriba bro")
                    ConsLog.exitMsg()
                    return False
            else:
                ConsLog.error("No se pudo crear la instalacion de la Junta, manda el error que sale arriba pai")
                ConsLog.exitMsg()
                return False
        else:
            ConsLog.error("No se pudo descargar el paquete de la Junta, manda el error que sale arriba pai")
            ConsLog.exitMsg()
            return False
    else:
        ConsLog.error("No se pudo crear el directorio de La Junta, manda el error que sale arriba pai")
        ConsLog.exitMsg()
        return False

    return True

def updateJunta():
    return False

def ReinstalacionFull():
    ConsLog.log("Empezando a reinstalar todos los archivos.")

    ConsLog.log("Eliminando directorio...")
    shutil.rmtree(juntaDir)
    ConsLog.logDone("Directorio eliminado")

    if instalacionInicial():
        return True
    else:
        return False

######################################################### INIT #########################################################

def init():
    try: 
        ConsLog.log("Buscando directorio de La Junta")
        with open(f"{modpackDownloadDir}/juntaData.json", "r") as tempFile:
            localJunta = json.load(tempFile)
            juntaLocalVersion = str(localJunta["localVersion"])
        ConsLog.logDone("Directorio encontrado.")

        # Comrpobar temporada de la junta
        ConsLog.log("Comrpobando temporada de La Junta...")
        if juntaLocalVersion[0] != juntaCloudVersion[0]:
            print("")
            ConsLog.warning(f"Hay una nueva temporada de la junta (La junta {juntaCloudVersion[0]})\nActualmente tienes instalado la temporada {juntaLocalVersion[0]}")
            ConsLog.log("Instalando nueva version...")
            if ReinstalacionFull():
                print("")
                ConsLog.logDone("Reinstalacion completa.")
                ConsLog.exitMsg()

        else:     
            # Comprobar que las versiones sean iguales
            ConsLog.logDone(f"Tienes la ultima temporada instalada! La junta {juntaLocalVersion[0]}")
            ConsLog.log(f"Verificando version de La Junta {juntaLocalVersion[0]}...")
            if juntaLocalVersion != juntaCloudVersion:
                print("")
                ConsLog.warning(f"Hay una nueva version de La Junta! ({juntaCloudVersion})\nActualmente tienes la {juntaLocalVersion}")
                updateJunta()
            else:
                print("")
                ConsLog.logDone("Ya tienes la ultima version de La Junta. " + juntaCloudVersion)
                ConsLog.tip('Si deseas reinstalar todo, escribe "res" EN MINUSCULAS, y presiona Enter, si no quieres reinstalar nada, ya puede cerrar el programa :)\n' + Fore.YELLOW + "TEN EN CUENTA QUE TODAS TUS CONFIGURACIONES, WAYPOINTS Y MAPA SE REINICIARAN (No perderas ningun objeto de tu inventario)")
                promptReinstall = input(">> ")
                if promptReinstall == "res":
                    if ReinstalacionFull():
                        print("")
                        ConsLog.logDone("Reinstalacion completa.")
                        ConsLog.exitMsg()
                else:
                    ConsLog.log("Seleccionaste no reinstalar.")
                    ConsLog.exitMsg()
    except:
        ConsLog.warning("No se encontró directorio de La Junta")
        instalacionInicial()


init()

# Que pregunte si quiere instalar o actualizar!!

# Detectar cuando hay un cambio en la temporada de la junta, por ejemplo de la Junta 2 (2.0) a la Junta Z (z0) comprobando el primer digito de la version. 
# version[0] y en caso que cambie, eliminar todos los archivos del .junta