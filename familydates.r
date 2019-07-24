data = read.csv('familydates.tmp')
data$date = as.Date(data$date)
pdf('familydates.pdf', 12, 8)
plot(c(0, nlevels(data$family)), c(as.Date('2006-12-31'), as.Date('2019-02-01')),
	pch='', xaxt='n', yaxt='n',
	xlab='ransomware family, sorted by average of first submission time',
	ylab='first submission date on VirusTotal',
	main='ransomware: estimated submission time by family')
years = 2006:2019
axis(2, as.Date(paste(years,'-06-30', sep='')), labels=years,
	tick=F, las=1, line=F)
axis(2, as.Date(paste(years,'-01-01', sep='')), labels=F)
abline(h=as.Date(paste(years,'-01-01', sep='')), col='#e0e0e0', lwd=.5)
boxplot(date ~ rank, data, lwd=.5, outcol='#7777ff', outcex=.3, outpch=4,
	whiskcol='#7777ff', staplecol='#7777ff', boxfill='#777777',
	boxlty=0, add=T, xaxt='n', yaxt='n')
