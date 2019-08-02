labels = read.csv('familydates1.tmp')
data = read.csv('familydates2.tmp')
data$date = as.Date(data$date)

pdf('familydates.pdf', 12, 8)
plot(c(3, max(labels$rank) - 2), c(as.Date('2007-07-31'), as.Date('2019-02-01')),
	pch='', xaxt='n', yaxt='n', xlab=NA,
	ylab='first submission date on VirusTotal',
	main='known ransomware: estimated submission time by family')

years = 2006:2019
axis(2, as.Date(paste(years,'-06-30', sep='')), labels=years,
	tick=F, las=1, line=F)
axis(2, as.Date(paste(years,'-01-01', sep='')), labels=F)
abline(h=as.Date(paste(years,'-01-01', sep='')), col='#cccccc', lwd=.5)
axis(1, at=labels$rank, labels=labels$family, las=2, cex.axis=.6)
abline(v=labels$rank, col='#cccccc', lwd=.5, lty=2)

boxplot(date ~ rank, data, lwd=.5, outcol='#7777ff', outcex=.3, outpch=4,
	whiskcol='#7777ff', staplecol='#7777ff', boxfill='#777777',
	boxlty=0, add=T, xaxt='n', yaxt='n')
