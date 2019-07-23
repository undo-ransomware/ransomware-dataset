data = read.csv('filedates.tmp')
data$date = as.Date(data$date)
pdf('filedates.pdf', 12, 8)
plot(c(0, max(data$filename)), c(as.Date('2006-12-31'), as.Date('2019-01-01')),
	pch='', xaxt='n', yaxt='n',
	xlab='VirusShare torrent number', ylab='first submission date on VirusTotal',
	main='ransomware: estimated submission time by VirusShare download file')
axis(1)
years = 2006:2019
axis(2, as.Date(paste(years,'-07-31', sep='')), labels=years,
	tick=F, las=1, line=F)
axis(2, as.Date(paste(years,'-01-01', sep='')), labels=F)
abline(h=as.Date(paste(years,'-01-01', sep='')), col='#e0e0e0', lwd=.5)
boxplot(date ~ filename, data, lwd=.5, outcol='#7777ff', outcex=.3,
	whiskcol='#777777', staplecol='#777777', boxfill='#cccccc',
	boxlty=0, add=T, xaxt='n', yaxt='n')
