import customtkinter
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date, timedelta
import threading
from CTkMessagebox import CTkMessagebox
#Default watchlist dictionary
watchlistDict = {'AAPL': None, 
                 'TSLA': None,
                 'IWM': None, 
                 'SPY': None,
                 'QQQ': None}
#Getting default info from API for watchlist
def updateDictValues():
    for ticker, price in watchlistDict.items():
        if price is None:
            try:
                info = yf.Ticker(ticker)
                watchlistDict[ticker] = info.info['previousClose']
            except:
                print('Error')               
updateDictValues()
    
#Initial window setup
root = customtkinter.CTk()
root.geometry("800x550")
root.minsize(800, 550)
root.maxsize(800, 550)
root._set_appearance_mode("Dark")
root.title("Stock Market")

#Configuring grid weights for root
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=3)

#Creating the main two frames
mainFrame = customtkinter.CTkFrame(root, fg_color="#2e3233")
mainFrame.grid(row=0, column=1, columnspan=2, sticky='nsew')

leftFrame = customtkinter.CTkFrame(root, fg_color="#242726")
leftFrame.grid(row=0, column=0, sticky='nsew')

#Configuring grid weights for mainFrame + leftFrame
mainFrame.columnconfigure(0, weight=1)
mainFrame.columnconfigure(1, weight=1)
mainFrame.columnconfigure(2, weight=1)
leftFrame.columnconfigure(0, weight=1)

#Frame within mainFrame to hold graphs
chartFrame = customtkinter.CTkFrame(mainFrame, fg_color="#2e3233")
chartFrame.grid(row=1, column=0, columnspan=3)

# Init fig
fig = plt.figure(figsize=(15,10), facecolor='#2e3233')
chartCanvas = FigureCanvasTkAgg(fig, master=chartFrame)
chartCanvas.get_tk_widget().pack(fill=customtkinter.BOTH, expand=True)


#Creating lambda functions with different index numbers for each watchlist remove button
def createDeleteCmd(ticker):
    return lambda: deleteCmd(ticker)
def deleteCmd(ticker):
    del watchlistDict[ticker]
    updateWatchlist()

def createAddCmd(ticker):
    return lambda: addCmd(ticker)
def addCmd(ticker):
    # ticker = chartName.cget('text')
    if ticker.upper() in watchlistDict:
        CTkMessagebox(master=root, title="Error", message="Stock Already in Watchlist", icon="cancel")
    else:
        watchlistDict[ticker] = None
        updateDictValues()
        updateWatchlist()
    
def updateWatchlist():
    #Delete elements from old watchlist
    for widget in leftFrame.winfo_children():
        widget.destroy()

    watchlistLabel = customtkinter.CTkLabel(leftFrame, text="Watchlist", font=('Helvetica', 16))
    watchlistLabel.pack()

    #Iterating through watchlistArray to make updated watchlist panel
    for ticker, price in watchlistDict.items():
        frame = customtkinter.CTkFrame(leftFrame, fg_color="#2e3233")
        # frame.bind("<Button-1>", test)
        frame.pack(fill = customtkinter.BOTH, padx=5, pady=2)
        # frame.grid(row=index+1, column=0, padx=5, pady=2, sticky="EW")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        stockNameLabel = customtkinter.CTkLabel(frame, text=ticker.upper(), font=('Helvetica', 16))
        stockNameLabel.grid(row=0, column=0, sticky='W', padx=5, pady=10)

        closePrice = price

        stockPriceLabel = customtkinter.CTkLabel(frame, text=closePrice)
        stockPriceLabel.grid(row=0, column=1, sticky='E', padx=5)

        deleteBtn = customtkinter.CTkButton(frame, text="Remove", width=40, command = createDeleteCmd(ticker))
        deleteBtn.grid(row=0, column=2, sticky="E", rowspan=2)

updateWatchlist()


searchLabel = customtkinter.CTkLabel(mainFrame, text="Search Stocks:")
searchLabel.grid(column=0, row=0, sticky="E", pady=20)

def searchCmd(event=None):
    if len(stockList) < 5:
        ticker = tickerEntry.get().upper()
        stockList.append(ticker)
        graphData()
        tickerEntry.delete(0, customtkinter.END)

    else:
        CTkMessagebox(master=root, title="Error", message="Graph Limit Reached (5/5)", icon="cancel")

tickerEntry = customtkinter.CTkEntry(mainFrame, placeholder_text="Ticker Symbol")
tickerEntry.bind('<Return>', command=searchCmd)
tickerEntry.grid(column=1, row=0, sticky="W", padx=8)

graphBtn = customtkinter.CTkButton(mainFrame, text="Graph", command=searchCmd)
graphBtn.grid(column=2, row=0, sticky='W')

chartKeyFrame = customtkinter.CTkFrame(mainFrame, fg_color="#2e3233")
chartKeyFrame.grid(row=2, column=0, columnspan=3, sticky='nsew')

#setting default style
plt.rcdefaults()
plt.rcParams.update({'axes.facecolor':'#2e3233', 
                     'axes.edgecolor':'white',
                     'axes.labelcolor':'white',
                     'axes.titlecolor':'white'
                     })
stockList = ['AAPL', 'TSLA', 'SPY']
#Creating lambda functions with different index numbers for each graph remove button
def createRemoveGraph(ticker):
    return lambda: removeGraph(ticker)
def removeGraph(ticker):
    stockList.remove(ticker)
    graphData()

def updateGraphData():
    try:
        endDate = date.today()
        startDate = endDate - timedelta(days=365)
        if len(stockList) > 0:
            for index, ticker in enumerate(stockList):
                #Get data, scale price, + plot data
                tickerData = yf.download(ticker, start=startDate, end=endDate)
                scaledPrice = ((tickerData['Close'] / tickerData['Close'].iloc[0]) -1) *100
                plt.plot(tickerData.index, scaledPrice, label=ticker)

                #Update GUI
                keyFrameChild = customtkinter.CTkFrame(chartKeyFrame, fg_color="#2e3233")
                keyFrameChild.grid(row=0, column=index, sticky="EW", padx=30)

                label = customtkinter.CTkLabel(keyFrameChild, text=ticker.upper())
                label.grid(row=0, column=0)
                removeBtn = customtkinter.CTkButton(keyFrameChild, text="Remove", width=10, command=createRemoveGraph(ticker), font=('Helvetica', 12), height=6)
                removeBtn.grid(row=1, column=0)
                watchBtn = customtkinter.CTkButton(keyFrameChild, text="Watchlist", width=20, font=('Helvetica', 12), height=6, command= createAddCmd(ticker))
                watchBtn.grid(row=2, column=0)
        
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.title(f'{ticker} Stock Price - 12 Month')
        plt.grid()
        plt.legend(loc='lower left', fontsize='large', labelcolor='white')

        # Customize the appearance of the plot
        plt.tick_params(colors="white")  # Set the color of the tick marks
        plt.xticks(color="white")   # Set the color of the x-axis tick labels
        plt.yticks(color="white")   # Set the color of the y-axis tick labels

    except Exception as e:
        print("e")
    
    chartCanvas.draw()


def graphData():
    #Clear old graph
    plt.cla()
    #Delete elements from old graph
    for widget in chartKeyFrame.winfo_children():
        widget.destroy()

    threading.Thread(target=updateGraphData).start()

graphData()

#test label
root.mainloop()
