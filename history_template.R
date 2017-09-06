png("Hello.png")
options(scipen=999)
savefont <- par(family="Charter")
{args}
y_min <- min(c(avg_put, price))
y_max <- max(c(avg_call, price))
plot(c(max(dte),min(dte)), c(y_min,y_max),
	 xlim=rev(range(dte)), 
     type="n", xlab="time", ylab="price",
     main="{month} {commodity} Option Market vs Averages")
lines(dte, avg_call, col="red")
lines(dte, avg_put, col="darkblue")
lines(dte, avg_opt, col="purple")
lines(dte, price, col="green")
legend("bottom", 
       legend=c("Avg Call", "Avg Put", "Avg Option", "Price"),
       bty="n",
       fill=c("red", "darkblue", "purple", "green"),
       horiz=TRUE)
dev.off()
