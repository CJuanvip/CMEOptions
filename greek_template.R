png("{symbol}_{month}_{greek}.png")
options(scipen=999)
{args}
y_min <- min(c(calls,puts))
y_max <- max(c(calls,puts,calls+puts))
plot(c(min(price),max(price)), c(y_min,y_max),
     type="n", xlab="Price", ylab="{greek}",
     main="{month} {commodity} Option Market Total {greek}")
lines(price, calls, col="red")
lines(price, puts, col="darkblue")
lines(price, calls+puts, col="purple")
legend("bottom",
       legend=c("Call {greek}", "Put {greek}", "Total {greek}"),
       bty="n",
       fill=c("red", "darkblue", "purple"),
       horiz=TRUE)
dev.off()
