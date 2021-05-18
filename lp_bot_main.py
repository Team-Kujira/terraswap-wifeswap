import http.client
import requests
import urllib3.exceptions
from terra_sdk.client.lcd import LCDClient
from terra_sdk.exceptions import LCDResponseError
from time import sleep

bot_token = 'xxxxxxxxx'

terra = LCDClient(chain_id="columbus-4", url="https://lcd.terra.dev")

swap_amount = 10
percent = 5

terra.tx.search()

def get_exchange_rate(amount):
    contract = "terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p"
    result = terra.wasm.contract_query(
        contract,
        {
            "simulation": {
                "offer_asset": {
                    "amount": str(amount * 1000000),
                    "info": {
                        "native_token": {
                            "denom": "uluna"
                        }
                    }
                }
            }
        }
    )
    return result


def telegram_bot_command():
    get = 'https://api.telegram.org/bot' + bot_token + '/getUpdates?offset=-1&limit=2&timeout=10'
    response = requests.get(get)
    return response.json()


def telegram_bot_sendtext(bot_message, chat_id):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' \
                + str(chat_id) + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


msg_id = 0
count = 0
bot_chat_ids = ["-1001488852663"]

while True:
    try:
        bot = telegram_bot_command()
        chat_id = bot['result'][0]['message']['chat']['id']
        if chat_id not in bot_chat_ids:
            bot_chat_ids.append(chat_id)
        if 'text' in bot['result'][0]['message'].keys():
            if bot['result'][0]['message']['message_id'] != msg_id:
                command = bot['result'][0]['message']['text']
                print(command)
                if command == '/swap' or command == '/swap@terralp_bot':
                    try:
                        return_amount = int(get_exchange_rate(swap_amount)['return_amount'])
                        exchange_rate = round(return_amount * 100 / (swap_amount * 1000000) - 100, 3)
                        if exchange_rate >= 0:
                            telegram_bot_sendtext("Current Luna -> bLuna exchange rate is: ~" + str(exchange_rate)
                                                  + "%\n\n" + str(swap_amount) + " Luna --> "
                                                  + str(round(return_amount / 1000000, 3)) + " bLuna"
                                                  + "\n\n app.terraswap.io", chat_id)
                        elif exchange_rate < 0:
                            telegram_bot_sendtext("Current bLuna -> Luna exchange rate is: ~" + str(exchange_rate * -1)
                                                  + "%\n\n" + str(round(return_amount / 1000000, 3))
                                                  + " bLuna --> " + str(swap_amount) + " Luna"
                                                  + "\n\n app.terraswap.io", chat_id)
                    except LCDResponseError as err:
                        print(err)
                        print("\nZzzzz...")
                        sleep(10)
                        print("Good nap, gonna try again now...\n")
                        continue
                    except ConnectionError:
                        print("Connection error...")
                        continue
                    except KeyError as k:
                        print("Couldn't find key: " + str(k))
                        continue
                    except requests.exceptions.ConnectionError:
                        print("Xonnection error")
                        continue
                    except urllib3.exceptions.ProtocolError:
                        print("Protocol error")
                        continue
                    except http.client.RemoteDisconnected:
                        print("Remote disconnected")
                elif command == '/info' or command == '/info@terralp_bot':
                    try:
                        telegram_bot_sendtext("Hallo!\n\nI'm a simple bot.\n\nYou can use '/swap' to get the current "
                                              "Luna:bLuna exchange rate on Terraswap.\nI will also alert "
                                              "everybody automatically when the swap rate is greater than 5% in "
                                              "either direction."
                                              "\n\n**NOTES**\n"
                                              "1. My rates do not take either tx commission (it's always ~0.003%),"
                                              " nor slippage into account "
                                              "– the swap simulation on Terraswap doesn't return slippage"
                                              "/minimum received. So, although the given spread is not exactly the one a real swap"
                                              " would have, it serves as a rough estimate!"
                                              "\n2. High swap rates are usually very short-lasting, "
                                              "often under a minute. I'm constantly simulating swaps on "
                                              "Terraswap to get the current exchange rate, so please don't blame me if "
                                              "the rate is lower by the time you make it to Terraswap!", chat_id)
                    except LCDResponseError as err:
                        print(err)
                        print("\nZzzzz...")
                        sleep(10)
                        print("Good nap, gonna try again now...\n")
                        continue
                    except ConnectionError:
                        print("Connection error...")
                        continue
                    except KeyError as k:
                        print("Couldn't find key: " + str(k))
                        continue
                    except requests.exceptions.ConnectionError:
                        print("Xonnection error")
                        continue
                    except urllib3.exceptions.ProtocolError:
                        print("Protocol error")
                        continue
                    except http.client.RemoteDisconnected:
                        print("Remote disconnected")
            msg_id = bot['result'][0]['message']['message_id']
        print("Attempt #" + str(count))
        return_amount = int(get_exchange_rate(swap_amount)['return_amount'])
        exchange_rate = round(return_amount * 100 / (swap_amount * 1000000) - 100, 3)
        if exchange_rate >= percent:
            print("GO! Exchange is: " + str(exchange_rate) + "%")
            for i in bot_chat_ids:
                telegram_bot_sendtext("GO GO GO! Swap gains: ~" + str(exchange_rate) + "%\n\n"
                                  + str(swap_amount) + " Luna -> " + str(round(return_amount / 1000000, 3)) + " bLuna"
                                      + "\n\n app.terraswap.io", i)
            sleep(666)
            count += 1
        elif exchange_rate <= percent * -1:
            print("GO! Exchange is: " + str(exchange_rate) + "%")
            for i in bot_chat_ids:
                telegram_bot_sendtext("GO GO GO! Swap gains: ~" + str(exchange_rate * -1) + "%\n\n"
                                  + str(round(return_amount / 1000000, 3)) + " bLuna -> " + str(swap_amount) + " Luna"
                                      + "\n\n app.terraswap.io", i)
            sleep(666)
            count += 1
        else:
            count += 1
        sleep(.666)
    except:
        print("err")
    # except ConnectionError:
    #     print("Connection error...")
    # except KeyError as k:
    #     print("Couldn't find key: " + str(k))
    # except LCDResponseError as err:
    #     print(err)
    #     print("\nZzzzz...")
    #     sleep(10)
    #     print("Good nap, gonna try again now...\n")
