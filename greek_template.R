png("{symbol}_{month}_{greek}.png")
options(scipen=999)
savefont <- par(family="Charter")
{args}
y_min <- min(c(calls,puts))
y_max <- max(c(calls,puts,calls+puts))
plot(c(min(price),max(price)), c(y_min,y_max),
     type="n", xlab="Price", ylab="{greek}", 
     main="{month} {commodity} Option Market Total {greek}")
lines(price, calls, col="#6689cc")
lines(price, puts, col="#472311")
lines(price, calls+puts, col="red")
legend("bottom", 
       legend=c("Call {greek}", "Put {greek}", "Total {greek}"),
       bty="n",
       fill=c("#6689cc", "#472311", "red"),
       horiz=TRUE)
dev.off()

