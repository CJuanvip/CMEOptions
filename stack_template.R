png("{symbol}_{month}_{graph}.png")
options(scipen=999)
savefont <- par(family="Charter")
{args}
m <- matrix(c(price, calls, puts),
            nrow=3,
            byrow=TRUE)
barplot(m[2:3,],
        col=c("#6689cc","#472311"),
        xlab="Price",
        ylab="Contracts",
        names=m[1,],
        cex.axis=0.75,
        cex.names=0.75,
        las=2,
        main="{month} {commodity} {desc}")
legend("top", 
       legend=c("ITM Calls","ITM Puts"),
       bty="n",
       fill=c("#6689cc","#472311"))
dev.off()
