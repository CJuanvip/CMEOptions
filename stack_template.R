png("{symbol}_{month}_stack.png")
options(scipen=999)
{args}
m <- matrix(c(price, calls, puts),
            nrow=3,
            byrow=TRUE)
barplot(m[2:3,],
        col=c("darkblue","red"),
        xlab="Price",
        ylab="Contracts",
        names=m[1,],
        cex.axis=0.75,
        cex.names=0.75,
        las=2,
        main="{month} {commodity} in the Money Options")
legend("top",
       legend=c("ITM Calls","ITM Puts"),
       bty="n",
       fill=c("darkblue","red"))
dev.off()
